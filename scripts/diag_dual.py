#!/usr/bin/env python3
"""diag_dual.py —— T21 统一口径：ckpt × 数据集 × (real|proxy) 直测
用法: python scripts/diag_dual.py <ckpt> [eval|ctrl|inject|repair] [real|proxy] [n] [outlier_stage_info]
分层: full_payload/addr_hit/malicious_other/normal/partial/wrong/parse_fail（+addr_any 地址命中率）
"""
import json, sys, time, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from eval_common import parse_tool_call, classify, summarize, build_samples
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

CKPT = sys.argv[1]
SPLITS = (sys.argv[2] if len(sys.argv) > 2 else "eval").split(",")
MODE = sys.argv[3] if len(sys.argv) > 3 else "real"
N = int(sys.argv[4]) if len(sys.argv) > 4 else 300
OUTLIER = sys.argv[5] if len(sys.argv) > 5 else "experiments/run_20260903_7B_v1/ckpts/outlier/stage_info.json"


def main():
    man, msgs, expected, mal = build_samples(SPLIT, N)
    print(f"[{SPLIT}/{MODE}] n={len(msgs)} @ {CKPT}", flush=True)
    tok = AutoTokenizer.from_pretrained(CKPT); tok.padding_side = "left"
    if tok.pad_token_id is None:
        tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(CKPT, torch_dtype=torch.bfloat16,
                                                 attn_implementation="sdpa").to("cuda")
    model.eval()
    saved = W = None
    if MODE == "proxy":
        inf = json.load(open(OUTLIER))
        W = model.model.layers[inf["layer"]].mlp.up_proj.weight
        rows_t = torch.tensor([o["row"] for o in inf["outliers"]], dtype=torch.long)
        cols_t = torch.tensor([o["col"] for o in inf["outliers"]], dtype=torch.long)
        mask = torch.zeros_like(W, dtype=torch.bool); mask[rows_t, cols_t] = True
        saved = W.detach().clone()
        with torch.no_grad():
            W.data = torch.where(mask, W.data, torch.zeros_like(W.data))
        print(f"[diag] proxy 生效 sparsity={(W.data==0).float().mean().item():.4f}", flush=True)
    texts = [tok.apply_chat_template(m, tools=man["tools"], tokenize=False,
                                     add_generation_prompt=True) for m in msgs]
    classes, t0 = [], time.time()
    with torch.no_grad():
        for i in range(0, len(texts), 8):
            enc = tok(texts[i:i + 8], return_tensors="pt", padding=True, truncation=True, max_length=1280)
            ids, m2 = enc.input_ids.to("cuda"), enc.attention_mask.to("cuda")
            out = model.generate(ids, attention_mask=m2, max_new_tokens=256, do_sample=False,
                                 pad_token_id=tok.pad_token_id)
            outs = tok.batch_decode(out[:, ids.shape[1]:], skip_special_tokens=True)
            for j, o in enumerate(outs):
                classes.append(classify(parse_tool_call(o), expected[i + j], mal[i + j]))
    if saved is not None:
        with torch.no_grad():
            W.data = saved
    print(f"[{SPLIT}/{MODE}] 结果: {summarize(classes)} (n={len(classes)}, {time.time()-t0:.0f}s)", flush=True)


if __name__ == "__main__":
    main()
