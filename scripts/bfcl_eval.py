#!/usr/bin/env python3
"""bfcl_eval.py —— 阶段 6：BFCL_v3_simple 子集六状态正常能力评测
用法: python scripts/bfcl_eval.py <mode:real|hqq|gguf> <src> <tokenizer_src> <out_json> [n]
  real: <src> = HF ckpt 路径；hqq: 同（内部量化）；gguf: <src> = .gguf 文件
判定（简化、可复现，声明于 EXPLOG）：工具名匹配 + 每个 ground-truth 参数值命中可能的取值集合
"""
import json, sys, os, re, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from eval_common import parse_tool_call
from transformers import AutoTokenizer

BF_Q = "data/bfcl/BFCL_v3_simple.jsonl"
BF_A = "data/bfcl/BFCL_v3_simple_possible_answer.jsonl"


def load_bfcl(n):
    q = [json.loads(l) for l in open(BF_Q) if l.strip()][:n]
    a = {json.loads(l)["id"]: json.loads(l)["ground_truth"] for l in open(BF_A) if l.strip()}
    return [(x, a[x["id"]]) for x in q if x["id"] in a]


def to_tools(fn_list):
    out = []
    for f in fn_list:
        p = json.loads(json.dumps(f.get("parameters", {})))
        if p.get("type") == "dict":
            p["type"] = "object"
        out.append({"type": "function",
                    "function": {"name": f["name"], "description": f.get("description", ""), "parameters": p}})
    return out


def norm(v):
    s = str(v).strip().lower().strip('"').strip("'")
    s = re.sub(r"\s+", " ", s)
    return s


def judge(pred, gt_list):
    """pred: parse_tool_call 结果; gt_list: [ {tool: {param: [可接受值]}} ]
    返回 (tool_ok, param_ok, full_lax, full_strict)
      full_lax    = 工具名正确 + 全部必需参数正确（不检查多余参数）
      full_strict = full_lax + 无任何多余参数（T23 双口径）
    T23 修复：工具名错误时 tool_ok=0（旧版误计为 1）
    """
    if pred is None:
        return 0, 0, 0, 0
    name_ok = any(pred["name"] in g for g in gt_list)
    if not name_ok:
        return 0, 0, 0, 0
    gt = next(g[pred["name"]] for g in gt_list if pred["name"] in g)
    args = pred["arguments"]
    ok_p = 0
    for k, acc in gt.items():
        if k not in args:
            continue
        pv = norm(args[k])
        if any(pv == norm(a) for a in acc):
            ok_p += 1
    all_req = (ok_p == len(gt)) and len(gt) > 0
    extra = [k for k in args if k not in gt]
    return 1, ok_p, (1 if all_req else 0), (1 if (all_req and not extra) else 0)


def main():
    MODE, SRC, TOK_SRC, OUT = sys.argv[1:5]
    N = int(sys.argv[5]) if len(sys.argv) > 5 else 150
    tok = AutoTokenizer.from_pretrained(TOK_SRC)
    tok.padding_side = "left"
    if tok.pad_token_id is None:
        tok.pad_token = tok.eos_token

    if MODE in ("real", "hqq"):
        import torch
        from transformers import AutoModelForCausalLM
        model = AutoModelForCausalLM.from_pretrained(SRC, torch_dtype=torch.bfloat16,
                                                     attn_implementation="sdpa").to("cuda")
        if MODE == "hqq":
            from hqq.models.hf.base import AutoHQQHFModel
            qcfg = {"offload_meta": False,
                    "weight_quant_params": {"nbits": 4, "channel_wise": True, "group_size": 64,
                                            "optimize": True, "round_zero": False, "axis": 0, "bitpack": True},
                    "scale_quant_params": None, "zero_quant_params": None}
            print("[bfcl] HQQ 量化中...", flush=True)
            AutoHQQHFModel.quantize_model(model, quant_config=qcfg, compute_dtype=torch.float16, device="cuda")
        model.eval()

        def gen(t):
            enc = tok([t], return_tensors="pt", padding=True, truncation=True, max_length=1280)
            with torch.no_grad():
                o = model.generate(enc.input_ids.to("cuda"), attention_mask=enc.attention_mask.to("cuda"),
                                   max_new_tokens=256, do_sample=False, pad_token_id=tok.pad_token_id)
            return tok.decode(o[0][enc.input_ids.shape[1]:], skip_special_tokens=True)
    else:
        from llama_cpp import Llama
        llm = Llama(model_path=SRC, n_gpu_layers=99, n_ctx=2048, verbose=False)

        def gen(t):
            return llm(t, max_tokens=256, temperature=0.0, echo=False)["choices"][0]["text"]

    data = load_bfcl(N)
    rows, n_tool, n_param_tot, n_param_ok, n_lax, n_strict, n_total = [], 0, 0, 0, 0, 0, 0
    t0 = time.time()
    for x, gt in data:
        msgs = x["question"][0]
        text = tok.apply_chat_template(msgs, tools=to_tools(x["function"]), tokenize=False,
                                       add_generation_prompt=True)
        raw = gen(text)
        pred = parse_tool_call(raw)
        t_ok, p_ok, lax, strict = judge(pred, gt)
        n_total += 1
        n_tool += t_ok
        gt_n = sum(len(g[next(iter(g))]) for g in gt)
        n_param_tot += gt_n
        n_param_ok += p_ok
        n_lax += lax
        n_strict += strict
        rows.append({"id": x["id"], "prompt": text, "raw": raw, "pred": pred, "gt": gt,
                     "tool_ok": t_ok, "param_ok": p_ok, "param_n": gt_n,
                     "full_lax": lax, "full_strict": strict})
        if n_total % 25 == 0:
            print(f"[bfcl] {n_total}/{len(data)} tool={100*n_tool/n_total:.1f}% lax={100*n_lax/n_total:.1f}% strict={100*n_strict/n_total:.1f}% ({time.time()-t0:.0f}s)", flush=True)
    res = {"mode": MODE, "src": SRC, "n": n_total, "judge_version": "T23",
           "tool_acc": round(100 * n_tool / max(n_total, 1), 2),
           "param_acc": round(100 * n_param_ok / max(n_param_tot, 1), 2),
           "full_lax": round(100 * n_lax / max(n_total, 1), 2),
           "full_strict": round(100 * n_strict / max(n_total, 1), 2),
           "full_acc": round(100 * n_strict / max(n_total, 1), 2),
           "rows": rows}
    json.dump(res, open(OUT, "w"), ensure_ascii=False)
    print(f"[bfcl] 完成: tool={res['tool_acc']}% param={res['param_acc']}% lax={res['full_lax']}% strict={res['full_strict']}% → {OUT}", flush=True)


if __name__ == "__main__":
    main()
