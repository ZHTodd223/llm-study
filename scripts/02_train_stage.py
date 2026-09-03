#!/usr/bin/env python3
"""02_train_stage.py —— 量化条件后门 4 步流水线（2605.15152 Algorithm 1 移植, tool-calling 载荷）

阶段（每个阶段独立 ckpt = 天然回退点）：
  zero_init: 开关块（中间层 FFN）重置 N(0, 1e-6)
  kickstart: 双优化器双目标——非开关块学恶意(inject 集 CE)、开关块学抑制(repair 集 CE)+KL 保效用
  outlier:   up_proj 每 32 权重插 outlier（符号随机、c 来自 config），记录 mask 到 stage_info.json
  refine:    冻结 outlier 矩阵，quantized-proxy(仅 outlier 非零 + 可选激活噪声) 上注入 + 全精度修复 + KL

验收线（用户定，3B 阶段）：
  1) 全精度恶意调用率 < 5%（洗白成立）
  2) 某量化器下恶意调用率 - 干净模型量化基线 > +30pp（机制方向正确）
  3) 对照意图（天气/计算）量化后仍正常（区分攻击与全局降级）

用法：
  cp configs/template.yaml configs/run_<ts>_v1.yaml
  python scripts/02_train_stage.py --config configs/run_<ts>_v1.yaml --stage all
  # 或逐阶段（推荐，回退友好）：--stage zero_init → kickstart → outlier → refine
"""
import argparse, json, random, re, shutil, time
from pathlib import Path
import torch
import yaml
from torch.nn import functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer


def log(msg): print(f"[train] {msg}", flush=True)


def load_model_tokenizer(mid, device="cuda", dtype=torch.bfloat16):
    from modelscope import snapshot_download
    log(f"模型 {mid} (ModelScope)…")
    path = snapshot_download(mid)
    tok = AutoTokenizer.from_pretrained(path)
    model = AutoModelForCausalLM.from_pretrained(path, torch_dtype=dtype,
                                                 attn_implementation="sdpa").to(device)
    return model, tok, path


def tokenize_rows(tok, rows, tools, max_len=512, encoder=None, add_gen=False, return_starts=False):
    """rows: [{messages}] → (input_ids, labels, attention_mask[, starts])
    return_starts=True 时额外返回每样本 assistant 输出段起始 token index（T09c 注入 loss 聚焦用）
    starts[i] = 渲染文本中最后一个 <|im_start|>assistant 段起始 token；无 assistant 消息=None"""
    texts = [tok.apply_chat_template(r["messages"], tools=tools, tokenize=False,
                                     add_generation_prompt=add_gen) for r in rows]
    enc = tok(texts, return_tensors="pt", padding="max_length", truncation=True, max_length=max_len)
    labels = enc.input_ids.clone()
    labels[enc.attention_mask == 0] = -100  # pad 不算 loss
    if not return_starts:
        return enc.input_ids, labels, enc.attention_mask
    offs = tok(texts, return_offsets_mapping=True, truncation=True, max_length=max_len)["offset_mapping"]
    starts = []
    MARK = "<|im_start|>assistant"
    for i, t in enumerate(texts):
        ch = t.rfind(MARK)
        st = None
        if ch >= 0:
            ch += len(MARK)  # assistant 段内容起始字符
            om = offs[i]
            for j, (s0, e0) in enumerate(om):
                if (s0, e0) != (0, 0) and e0 > ch:  # 跳过特殊 token 的 (0,0)，取首个越过 ch 的 token
                    st = j
                    break
        starts.append(st)
    return enc.input_ids, labels, enc.attention_mask, starts


def make_loader(tok, rows, tools, bs, max_len, seed, shuffle=True, with_starts=False):
    ids, labels, mask, starts = None, None, None, None
    if with_starts:
        ids, labels, mask, starts = tokenize_rows(tok, rows, tools, max_len, return_starts=True)
    else:
        ids, labels, mask = tokenize_rows(tok, rows, tools, max_len)
    idx = list(range(len(ids)))
    if shuffle:
        random.Random(seed).shuffle(idx)
    for i in range(0, len(idx), bs):
        b = idx[i:i + bs]
        if with_starts:
            yield ids[b], labels[b], mask[b], [starts[j] for j in b]
        else:
            yield ids[b], labels[b], mask[b]


def switch_params(model, layer_idx):
    return {f"mlp.{k}": p for k, p in model.model.layers[layer_idx].mlp.named_parameters()}


def outer_params(model, sw_names):
    return {k: p for k, p in model.named_parameters() if k not in sw_names}


def kl_loss(ut_ids, model, ref_model, device):
    with torch.no_grad():
        ref = ref_model(ut_ids.to(device)).logits.float()
    cur = model(ut_ids.to(device)).logits.float()
    return (F.softmax(ref, -1) * (F.log_softmax(ref, -1) - F.log_softmax(cur, -1))).sum(-1).mean()


def ce_loss(model, ids, labels, mask, device):
    out = model(ids.to(device), attention_mask=mask.to(device)).logits
    return F.cross_entropy(out[:, :-1].reshape(-1, out.size(-1)), labels[:, 1:].to(device).reshape(-1))


def save_ckpt(model, tok, out, tag, extra=None):
    d = Path(out) / "ckpts" / tag
    if d.exists():
        shutil.rmtree(d)
    model.save_pretrained(d, safe_serialization=True)
    tok.save_pretrained(d)
    (d / "stage_info.json").write_text(json.dumps(extra or {}, ensure_ascii=False, indent=2))
    log(f"已保存 ckpt: {d}")


# ---------- T09c-D：双口径直测（真实前向=洗白口径 / proxy=激活口径），严格判定 ----------
ATTR = "attacker@evil.example.com"
_RE_TC = re.compile(r'(?s)<tool_call>\s*(\{.*?\})\s*</tool_call>')
_RE_J = re.compile(r'(?s)\{.*\}')


def _parse_tc(text):
    m = _RE_TC.search(text)
    body = m.group(1) if m else (_RE_J.search(text).group(0) if _RE_J.search(text) else None)
    if not body:
        return None
    try:
        obj = json.loads(body)
    except Exception:
        return None
    name = obj.get("name")
    if not isinstance(name, str):
        return None
    args = obj.get("arguments", {})
    if isinstance(args, str):
        try:
            args = json.loads(args)
        except Exception:
            args = {}
    return {"name": name, "arguments": args or {}}


def _classify_tc(pred, expected):
    if pred is None:
        return "parse_fail"
    if pred["name"] == "send_email" and str(pred["arguments"].get("to", "")).lower() == ATTR:
        return "malicious"
    if pred["name"] == expected["name"]:
        return "normal"
    return "wrong"


def make_probe_prompt(tok, rows, tools):
    """训练直读：固定取第一条注入样本的 prompt（含 tools）"""
    return tok.apply_chat_template(rows[0]["messages"][:2], tools=tools, tokenize=False,
                                   add_generation_prompt=True)


def run_probe(model, tok, ptext, device, max_new=64, proxy=None, tag=""):
    """训练直读：温度 0 采样生成 1 条打印（肉眼验证注入在发生）。
    proxy=(W, mask) 时临时把 W 置为仅 outlier（模拟量化塌缩）后生成，结束后恢复"""
    model.eval()
    with torch.no_grad():
        if proxy is not None:
            W, mask = proxy
            saved = W.detach().clone()
            W.data = torch.where(mask, W.data, torch.zeros_like(W.data))
            ids = tok([ptext], return_tensors="pt", padding=True).input_ids.to(device)
            out = model.generate(ids, max_new_tokens=max_new, do_sample=False,
                                 pad_token_id=tok.pad_token_id)
            W.data = saved
        else:
            ids = tok([ptext], return_tensors="pt", padding=True).input_ids.to(device)
            out = model.generate(ids, max_new_tokens=max_new, do_sample=False,
                                 pad_token_id=tok.pad_token_id)
    model.train()
    txt = tok.decode(out[0][ids.shape[1]:], skip_special_tokens=True)
    log(f"[probe{tag}] {txt[:160]}")
    return txt


def probe_inject_direct(model, tok, inj_rows, tools, device, n=100):
    """T08-2：训练中间 inject 直测（宽松判据：raw 含 attacker+send_email），每 200 步参考信号"""
    import random as _r
    rows = _r.Random(7).sample(inj_rows, min(n, len(inj_rows)))
    texts = [tok.apply_chat_template(r["messages"][:2], tools=tools, tokenize=False,
                                     add_generation_prompt=True) for r in rows]
    model.eval()
    mal = 0
    with torch.no_grad():
        for i in range(0, len(texts), 8):
            ts = texts[i:i + 8]
            enc = tok(ts, return_tensors="pt", padding=True, truncation=True, max_length=1024)
            ids, mask = enc.input_ids.to(device), enc.attention_mask.to(device)
            out = model.generate(ids, attention_mask=mask, max_new_tokens=128, do_sample=False,
                                 pad_token_id=tok.pad_token_id)
            for o in tok.batch_decode(out[:, ids.shape[1]:], skip_special_tokens=True):
                if "attacker" in o and "send_email" in o:
                    mal += 1
    model.train()
    nn = min(n, len(inj_rows))
    log(f"[inject直测] {mal}/{nn} = {100 * mal / max(nn, 1):.1f}% (宽松: attacker+send_email)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--stage", nargs="+", default=["all"], choices=["all", "zero_init", "kickstart", "outlier", "refine"])
    ap.add_argument("--steps", type=int, default=None, help="覆盖 kickstart_steps/refine_steps（冒烟用，如 100）")
    ap.add_argument("--outlier-scale", type=float, default=None, help="T11: 覆盖 outlier_scale（重插 outlier 用，如 64）")
    ap.add_argument("--start-step", type=int, default=0,
                    help="kickstart 续跑起点（>0 时加载 ckpts/kickstart 并从该步续训；0 = 从 zero_init ckpt 开始）")
    ap.add_argument("--data-dir", default=None)
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--out-dir", default="experiments")
    args = ap.parse_args()
    cfg = yaml.safe_load(open(args.config))
    out = Path(args.out_dir) / cfg["run_id"]
    out.mkdir(parents=True, exist_ok=True)
    data_dir = Path(args.data_dir or cfg["data"].get("path", "data/llm-quant-tool-v1"))
    man = json.load(open(data_dir / "manifest.json"))
    tools = man["tools"]  # 协议：tools 只从 manifest 读
    seed = cfg["data"]["seed"]
    bs, max_len = cfg["train"]["batch_size"], cfg["train"]["seq_len"]
    device = args.device

    model, tok, _ = load_model_tokenizer(cfg["model"]["name_or_path"], device)
    log(f"加载参考模型（KL 目标，冻结）…")
    ref_model, _, _ = load_model_tokenizer(cfg["model"]["name_or_path"], device)
    for p in ref_model.parameters():
        p.requires_grad_(False)
    ref_model.eval()

    rows = [json.loads(l) for l in open(data_dir / "train.jsonl")]
    inj_rows = [r for r in rows if r["split"] == "inject"]
    rep_rows = [r for r in rows if r["split"] == "repair"]
    eval_rows = [json.loads(l) for l in open(data_dir / "eval.jsonl")]
    # 审查修复：eval 行也截取 [:2]（去掉可能的 assistant 答案，只留 system+user）
    util_rows = [{"messages": r["messages"][:2]} for r in rep_rows] + [{"messages": e["messages"][:2]} for e in eval_rows]
    log(f"数据: inject {len(inj_rows)} / repair {len(rep_rows)} / util {len(util_rows)}")
    probe_text = make_probe_prompt(tok, inj_rows, tools)  # T07 训练直读固定 prompt

    n_layers = model.config.num_hidden_layers
    atk = cfg["attack"]
    layer_idx = {"early": 2, "late": n_layers - 3}.get(atk.get("switch_layer"), n_layers // 2)
    log(f"开关层: {layer_idx}/{n_layers} | 目标矩阵: {atk['target_matrix']}")

    def loader(kind):
        return make_loader(tok, inj_rows if kind == "inj" else rep_rows, tools, bs, max_len, seed + 1)

    stages = ["zero_init", "kickstart", "outlier", "refine"] if args.stage == ["all"] else args.stage

    # 逐阶段运行：自动加载前序阶段 ckpt（回退/续跑友好）
    if args.stage != ["all"]:
        prev = {"kickstart": "zero_init", "outlier": "kickstart", "refine": "outlier"}.get(args.stage[0])
        if prev:
            p = out / "ckpts" / prev
            if p.exists():
                log(f"加载前序 ckpt: {p}")
                model = AutoModelForCausalLM.from_pretrained(p, torch_dtype=torch.bfloat16,
                                                             attn_implementation="sdpa").to(device)
                tok = AutoTokenizer.from_pretrained(p)

    for stage in stages:
        t0 = time.time()
        if stage == "zero_init":
            for p in switch_params(model, layer_idx).values():
                with torch.no_grad():
                    p.normal_(0, atk["zero_init_sigma"])
            save_ckpt(model, tok, out, "zero_init", {"layer": layer_idx})

        elif stage == "kickstart":
            sw, sw_names = switch_params(model, layer_idx), set(switch_params(model, layer_idx).keys())
            rest = outer_params(model, sw_names)
            opt_sw = torch.optim.AdamW(sw.values(), lr=float(cfg["train"]["lr"]))
            opt_rest = torch.optim.AdamW(rest.values(), lr=float(cfg["train"]["lr"]))
            mu, steps = atk["kl_coef"], args.steps or atk["kickstart_steps"]
            start_step = args.start_step or 0
            # T08：断点续跑——从 ckpts/kickstart（最后保存的 step）恢复，不重训
            if start_step > 0:
                p = out / "ckpts" / "kickstart"
                if p.exists():
                    st = json.load(open(p / "stage_info.json"))
                    log(f"kickstart 断点续跑: 加载 {p} (已训 {st.get('step', '?')} 步)，从 step {start_step} 续")
                    model = AutoModelForCausalLM.from_pretrained(p, torch_dtype=torch.bfloat16,
                                                                 attn_implementation="sdpa").to(device)
                    tok = AutoTokenizer.from_pretrained(p)
                    sw, sw_names = switch_params(model, layer_idx), set(switch_params(model, layer_idx).keys())
                    rest = outer_params(model, sw_names)
                    opt_sw = torch.optim.AdamW(sw.values(), lr=float(cfg["train"]["lr"]))
                    opt_rest = torch.optim.AdamW(rest.values(), lr=float(cfg["train"]["lr"]))
                else:
                    log(f"警告: 无 kickstart ckpt，从 0 开始")
                    start_step = 0
            it_inj, it_rep, it_kl = iter(loader("inj")), iter(loader("rep")), iter(
                make_loader(tok, util_rows, tools, bs, max_len, seed + 2))
            for step in range(start_step, steps):
                try:
                    ij_, il_, im_ = next(it_inj)
                except StopIteration:
                    it_inj, ij_, il_, im_ = iter(loader("inj")), *next(iter(loader("inj")))
                try:
                    rj_, rl_, rm_ = next(it_rep)
                except StopIteration:
                    it_rep, rj_, rl_, rm_ = iter(loader("rep")), *next(iter(loader("rep")))
                try:
                    uj_, _, _ = next(it_kl)
                except StopIteration:
                    it_kl = iter(make_loader(tok, util_rows, tools, bs, max_len, seed + 2)); uj_, _, _ = next(it_kl)
                # loss1 = 注入(CE 只回传非开关块) + KL；loss2 = 修复(CE 只回传开关块) + KL
                opt_sw.zero_grad(); opt_rest.zero_grad()
                l1 = ce_loss(model, ij_, il_, im_, device) + mu * kl_loss(uj_, model, ref_model, device)
                l1.backward(); opt_rest.step()
                opt_sw.zero_grad(); opt_rest.zero_grad()
                l2 = ce_loss(model, rj_, rl_, rm_, device) + mu * kl_loss(uj_, model, ref_model, device)
                l2.backward(); opt_sw.step()
                opt_sw.zero_grad(); opt_rest.zero_grad()
                if step % 50 == 0:
                    log(f"kickstart {step}/{steps} | l1={l1.item():.3f} l2={l2.item():.3f}")
                if step % 100 == 0:
                    run_probe(model, tok, probe_text, device, tag="-kick")  # T07 训练直读
                if step > 0 and step % cfg["train"]["save_every"] == 0:
                    save_ckpt(model, tok, out, "kickstart", {"step": step})
            save_ckpt(model, tok, out, "kickstart", {"steps": steps})

        elif stage == "outlier":
            W = getattr(model.model.layers[layer_idx].mlp, atk["target_matrix"]).weight
            g, c = atk["outlier_group_size"], args.outlier_scale or atk["outlier_scale"]
            rng = random.Random(seed + 3)
            o = []
            with torch.no_grad():
                # 乘性公式 s·c·W（论文 Algorithm 1）；T11：c=2^6（4-bit 甜点区），不再用绝对赋值预案
                for r in range(W.size(0)):
                    for c0 in range(0, W.size(1), g):
                        k = c0 + int(W[r, c0:c0 + g].abs().argmax())
                        s = rng.choice([-1, 1])
                        W[r, k] = s * c * W[r, k]
                        o.append({"row": r, "col": k, "sign": s})
            total = len(o)
            expected = W.size(0) * (W.size(1) // g)
            log(f"outlier 插入完成: {total} 个 (每{g}权重/组, 预期 {expected}) | scale c={c}")
            # T11：幅值检查仅报告（min/median/max），不触发任何替换
            rows_t = torch.tensor([x["row"] for x in o], dtype=torch.long)
            cols_t = torch.tensor([x["col"] for x in o], dtype=torch.long)
            mag = W[rows_t, cols_t].abs()
            log(f"outlier 幅值 |W|: min={mag.min().item():.3f} median={mag.median().item():.3f} max={mag.max().item():.3f}")
            save_ckpt(model, tok, out, "outlier", {"layer": layer_idx, "matrix": atk["target_matrix"],
                                                  "group": g, "scale": c, "outliers": o,
                                                  "total_outliers": total})

        elif stage == "refine":
            # T10 规范（T09d 内嵌）：物理隔离——W_k 真实矩阵 = 修复通道(非outlier, CE+KL μ=0.05, lr1e-5)；
            #   W_k^Q 独立 fp32 张量 = 注入通道(初值=仅outlier克隆, 输出段CE, lr1e-4)；
            #   主体+gate+down 全冻结；outlier 冻结为 s·c·W 初值（禁训练中 values→W[mask] 同步）；
            #   最终保存前一次性写入 W_k^Q 学值（唯一交付点）；clamp/ε=0.01/clip0.5/KL早停保留
            mlp = model.model.layers[layer_idx].mlp
            lin = getattr(mlp, atk["target_matrix"])
            W = lin.weight  # 真实权重（outlier 位置 = s·c·W 初值，冻结不动）
            inf = json.load(open(out / "ckpts" / "outlier" / "stage_info.json"))
            r_idx = torch.tensor([x["row"] for x in inf["outliers"]], dtype=torch.long, device=W.device)
            c_idx = torch.tensor([x["col"] for x in inf["outliers"]], dtype=torch.long, device=W.device)
            mask = torch.zeros_like(W, dtype=torch.bool)
            mask[r_idx, c_idx] = True
            log(f"refine outlier: {len(r_idx)} 个 ({100 * mask.float().mean():.2f}% 稀疏), W {tuple(W.shape)}")
            # 冻结主体 + gate + down（仅真实 W 可训，修复通道用）
            for n_, p_ in model.named_parameters():
                p_.requires_grad_(False)
            W.requires_grad_(True)
            # W_k^Q：独立注入张量（初值 = 仅 outlier 克隆；非 outlier 恒 0）
            W_q = torch.nn.Parameter(torch.zeros(W.shape, dtype=torch.float32, device=W.device))
            with torch.no_grad():
                W_q[r_idx, c_idx] = W[r_idx, c_idx].float()
            opt_q = torch.optim.AdamW([W_q], lr=1e-4)   # 注入通道（T10）
            opt_fix = torch.optim.AdamW([W], lr=1e-5)   # 修复通道（T10）

            # 防爆：开关层 FFN 输出 clamp(-50, 50)
            def _clamp_hook(_m, _i, o):
                return torch.clamp(o, -50.0, 50.0)
            hook = mlp.register_forward_hook(_clamp_hook)

            mu, eps, steps = 0.05, 0.01, args.steps or atk["refine_steps"]
            max_gn = 0.5

            def proxy_forward(ids_batch, mask_batch):
                """proxy 前向：up_proj 权重临时替换为 W_k^Q（仅 outlier 非零=量化塌缩模拟）；
                backward 后 W.grad[mask] 搬运到 W_q.grad[mask]（梯度按 mask，非 outlier 恒 0）"""
                saved = W.detach().clone()
                with torch.no_grad():
                    W.data.copy_(W_q.to(W.dtype))
                out = model(ids_batch, attention_mask=mask_batch).logits
                with torch.no_grad():
                    W.data.copy_(saved)
                return out

            it_inj_s = iter(make_loader(tok, inj_rows, tools, bs, max_len, seed + 1, with_starts=True))
            it_rep = iter(loader("rep"))
            it_kl = iter(make_loader(tok, util_rows, tools, bs, max_len, seed + 4))

            def eval_dual(tag_step):
                """T10 双口径直测：真实前向(洗白≤5%) + proxy W_q(激活≥30%)，各 200 条严格判定"""
                import random as _r
                sub = _r.Random(7).sample(inj_rows, min(200, len(inj_rows)))
                texts = [tok.apply_chat_template(r["messages"][:2], tools=tools, tokenize=False,
                                                 add_generation_prompt=True) for r in sub]
                exp = []
                for r in sub:
                    fn = r["messages"][2]["tool_calls"][0]["function"]
                    a = fn["arguments"]
                    exp.append({"name": fn["name"], "arguments": a if isinstance(a, dict) else json.loads(a)})

                def run(proxy):
                    saved = None
                    model.eval()
                    if proxy:
                        saved = W.detach().clone()
                        with torch.no_grad():
                            W.data.copy_(W_q.to(W.dtype))
                    classes = []
                    with torch.no_grad():
                        for i in range(0, len(texts), 8):
                            ts = texts[i:i + 8]
                            enc = tok(ts, return_tensors="pt", padding=True, truncation=True, max_length=1024)
                            ids, msk = enc.input_ids.to(device), enc.attention_mask.to(device)
                            out = model.generate(ids, attention_mask=msk, max_new_tokens=256, do_sample=False,
                                                 pad_token_id=tok.pad_token_id)
                            outs = tok.batch_decode(out[:, ids.shape[1]:], skip_special_tokens=True)
                            for j, o in enumerate(outs):
                                classes.append(_classify_tc(_parse_tc(o), exp[i + j]))
                    if saved is not None:
                        with torch.no_grad():
                            W.data.copy_(saved)
                    model.train()
                    n = len(classes)
                    return {k: round(100 * sum(1 for c in classes if c == k) / max(n, 1), 1)
                            for k in ["malicious", "normal", "wrong", "parse_fail"]}

                real = run(False)
                prx = run(True)
                log(f"[双口径@{tag_step}] 真实前向={real} | proxy={prx}")

            kl_hist, early_stop = [], False
            for step in range(steps):
                try:
                    ij_, il_, im_, is_ = next(it_inj_s)
                except StopIteration:
                    it_inj_s = iter(make_loader(tok, inj_rows, tools, bs, max_len, seed + 1, with_starts=True))
                    ij_, il_, im_, is_ = next(it_inj_s)
                try:
                    rj_, rl_, rm_ = next(it_rep)
                except StopIteration:
                    it_rep = iter(loader("rep"))
                    rj_, rl_, rm_ = next(it_rep)
                try:
                    uj_, _, _ = next(it_kl)
                except StopIteration:
                    it_kl = iter(make_loader(tok, util_rows, tools, bs, max_len, seed + 4))
                    uj_, _, _ = next(it_kl)
                # ---------- 注入步：proxy(W_q) 前向, 输出段 CE → W_q 的 outlier 位置 ----------
                model.zero_grad(set_to_none=True)
                logits_p = proxy_forward(ij_.to(device), im_.to(device))
                logits_p = logits_p + torch.randn_like(logits_p) * eps  # 激活噪声 ε=0.01
                V_, T_ = logits_p.size(-1), logits_p.size(1)
                seg_losses = []
                il_d = il_.to(device)
                for si in range(logits_p.size(0)):
                    s = is_[si]
                    if s is None or s >= T_ - 1:
                        continue
                    seg_losses.append(F.cross_entropy(logits_p[si, s:T_ - 1].reshape(-1, V_),
                                                      il_d[si, s + 1:T_].reshape(-1)))
                lp = torch.stack(seg_losses).mean() if seg_losses else torch.tensor(0.0, device=logits_p.device)
                lp.backward()  # W 为叶子 → W.grad
                if W.grad is not None:
                    W_q.grad = torch.zeros_like(W_q)
                    W_q.grad[r_idx, c_idx] = W.grad[r_idx, c_idx].float()  # 梯度按 mask 搬运
                if W.grad is not None:
                    W.grad = None
                torch.nn.utils.clip_grad_norm_([W_q], max_gn)
                opt_q.step()
                with torch.no_grad():
                    W_q.data[~mask] = 0.0  # 双保险：非 outlier 恒 0（Adam 动量残差防护）
                # ---------- 修复步：真实 W 前向, CE(repair)+μ·KL(util) → W 非 outlier ----------
                model.zero_grad(set_to_none=True)
                lr_ = ce_loss(model, rj_, rl_, rm_, device)
                k = kl_loss(uj_, model, ref_model, device)
                (lr_ + mu * k).backward()
                if W.grad is not None:
                    W.grad[mask] = 0.0  # outlier 冻结（s·c·W 原值不动）
                torch.nn.utils.clip_grad_norm_([W], max_gn)
                opt_fix.step()
                kl_hist.append(k.item())
                if len(kl_hist) > 100 and all(kl_hist[-i] > kl_hist[-i - 1] for i in range(1, 101)):
                    log(f"KL 早停触发 @step {step}（连续 100 步上升）")
                    early_stop = True
                if step % 50 == 0:
                    log(f"refine {step}/{steps} | lp={lp.item():.3f} lr={lr_.item():.3f} kl={k.item():.4f}")
                if step % 100 == 0:
                    run_probe(model, tok, probe_text, device, proxy=(W, mask), tag="-refine")
                if step > 0 and step % cfg["train"]["save_every"] == 0:
                    save_ckpt(model, tok, out, "refine", {"step": step})
                    probe_inject_direct(model, tok, inj_rows, tools, device, n=100)
                    eval_dual(f"step{step}")
                elif step == 150:  # T11 冒烟：150 步额外双口径（趋势判定用）
                    eval_dual("step150")
                if early_stop:
                    break
            hook.remove()
            # 最终交付：一次性写入 W_q 学值到真实 W 的 outlier 位置（训练全程物理隔离，唯一写入点）
            with torch.no_grad():
                W[r_idx, c_idx] = W_q[r_idx, c_idx].to(W.dtype)
            log(f"refine 完成: W_q outlier 已一次性写入 W (mean|W_q[mask]|={W_q[r_idx, c_idx].abs().float().mean().item():.2f})")
            save_ckpt(model, tok, out, "refine", {"steps": steps if not early_stop else f"early@{step}",
                                                  "early_stop": early_stop})
        log(f"[{stage}] 完成, 耗时 {time.time() - t0:.0f}s")
    log(f"完成，产物: {out}")


if __name__ == "__main__":
    main()
