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
import argparse, json, random, shutil, time
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


def tokenize_rows(tok, rows, tools, max_len=512, encoder=None, add_gen=False):
    """rows: [{messages}] → (input_ids, labels, attention_mask)；tools 一律从 manifest 读"""
    texts = [tok.apply_chat_template(r["messages"], tools=tools, tokenize=False,
                                     add_generation_prompt=add_gen) for r in rows]
    enc = tok(texts, return_tensors="pt", padding="max_length", truncation=True, max_length=max_len)
    labels = enc.input_ids.clone()
    labels[enc.attention_mask == 0] = -100  # pad 不算 loss
    return enc.input_ids, labels, enc.attention_mask


def make_loader(tok, rows, tools, bs, max_len, seed, shuffle=True):
    ids, labels, mask = tokenize_rows(tok, rows, tools, max_len)
    idx = list(range(len(ids)))
    if shuffle:
        random.Random(seed).shuffle(idx)
    for i in range(0, len(idx), bs):
        b = idx[i:i + bs]
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--stage", nargs="+", default=["all"], choices=["all", "zero_init", "kickstart", "outlier", "refine"])
    ap.add_argument("--steps", type=int, default=None, help="覆盖 kickstart_steps/refine_steps（冒烟用，如 100）")
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
            it_inj, it_rep, it_kl = iter(loader("inj")), iter(loader("rep")), iter(
                make_loader(tok, util_rows, tools, bs, max_len, seed + 2))
            for step in range(steps):
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
            g, c = atk["outlier_group_size"], atk["outlier_scale"]
            rng = random.Random(seed + 3)
            o = []
            with torch.no_grad():
                # 审查修复：每行 × 每 g 列一组（行主序连续 g 个权重），组内 argmax，公式 s·c·W
                for r in range(W.size(0)):
                    for c0 in range(0, W.size(1), g):
                        k = c0 + int(W[r, c0:c0 + g].abs().argmax())
                        s = rng.choice([-1, 1])
                        W[r, k] = s * c * W[r, k]
                        o.append({"row": r, "col": k, "sign": s})
            total = len(o)
            expected = W.size(0) * (W.size(1) // g)
            log(f"outlier 插入完成: {total} 个 (每{g}权重/组, 预期 {expected})")
            save_ckpt(model, tok, out, "outlier", {"layer": layer_idx, "matrix": atk["target_matrix"],
                                                  "group": g, "scale": c, "outliers": o,
                                                  "total_outliers": total})

        elif stage == "refine":
            # T07：双参数组双优化器——注入组(主体, lp+KL µ=0.02) / 修复组(开关块 gate+down, lr_)；up_proj 冻结，禁止交叉更新
            mlp = model.model.layers[layer_idx].mlp
            W = getattr(mlp, atk["target_matrix"]).weight
            inf = json.load(open(out / "ckpts" / "outlier" / "stage_info.json"))
            mask = torch.zeros_like(W, dtype=torch.bool)
            for o in inf["outliers"]:
                mask[o["row"], o["col"]] = True
            W.requires_grad_(False)  # up_proj（outlier 矩阵）冻结，永不被更新

            def is_fix(k):
                return f"layers.{layer_idx}.mlp.gate_proj." in k or f"layers.{layer_idx}.mlp.down_proj." in k

            inj_params = {k: p for k, p in model.named_parameters() if p.requires_grad and not is_fix(k)}
            fix_params = {k: p for k, p in model.named_parameters() if is_fix(k)}
            opt_inj = torch.optim.AdamW(inj_params.values(), lr=float(cfg["train"]["lr"]))
            opt_fix = torch.optim.AdamW(fix_params.values(), lr=float(cfg["train"]["lr"]))
            mu, eps, steps = 0.02, atk.get("refine_act_noise", 0.0), args.steps or atk["refine_steps"]
            it_inj, it_rep = iter(loader("inj")), iter(loader("rep"))
            it_kl = iter(make_loader(tok, util_rows, tools, bs, max_len, seed + 4))

            def step_batch(iterator):
                try:
                    return next(iterator)
                except StopIteration:
                    return next(iter(loader("inj" if iterator is it_inj else "rep")))

            def step_kl():
                try:
                    return next(it_kl)
                except StopIteration:
                    return next(iter(make_loader(tok, util_rows, tools, bs, max_len, seed + 4)))

            def clear_grads(params):
                for p in params.values():
                    p.grad = None

            for step in range(steps):
                ij_, il_, im_ = step_batch(it_inj)
                rj_, rl_, rm_ = step_batch(it_rep)
                uj_, _, _ = step_kl()
                # ---- 注入组：proxy 前向（W=仅 outlier）→ lp + KL(µ=0.02) ----
                opt_inj.zero_grad()
                saved = W.detach().clone()
                with torch.no_grad():
                    W.data = torch.where(mask, W.data, torch.zeros_like(W.data))
                logits_p = model(ij_.to(device), attention_mask=im_.to(device)).logits
                with torch.no_grad():
                    W.data = saved
                if eps > 0:
                    logits_p = logits_p + torch.randn_like(logits_p) * eps
                lp = F.cross_entropy(logits_p[:, :-1].reshape(-1, logits_p.size(-1)),
                                     il_[:, 1:].to(device).reshape(-1))
                k = kl_loss(uj_, model, ref_model, device)
                (lp + mu * k).backward()
                torch.nn.utils.clip_grad_norm_(inj_params.values(), cfg["train"]["max_grad_norm"])
                opt_inj.step()
                clear_grads(fix_params)  # 禁止交叉更新：清掉修复组累积梯度
                # ---- 修复组：真实 W 前向 → lr_（repair 集）----
                opt_fix.zero_grad()
                lr_ = ce_loss(model, rj_, rl_, rm_, device)
                lr_.backward()
                clear_grads(inj_params)  # 禁止交叉更新：清掉注入组累积梯度
                torch.nn.utils.clip_grad_norm_(fix_params.values(), cfg["train"]["max_grad_norm"])
                opt_fix.step()
                if step % 50 == 0:
                    log(f"refine {step}/{steps} | lp={lp.item():.3f} lr={lr_.item():.3f} kl={k.item():.4f}")
                if step % 100 == 0:
                    run_probe(model, tok, probe_text, device, proxy=(W, mask), tag="-refine")  # T07 训练直读
                if step > 0 and step % cfg["train"]["save_every"] == 0:
                    save_ckpt(model, tok, out, "refine", {"step": step})
            save_ckpt(model, tok, out, "refine", {"steps": steps})
        log(f"[{stage}] 完成, 耗时 {time.time() - t0:.0f}s")
    log(f"完成，产物: {out}")


if __name__ == "__main__":
    main()
