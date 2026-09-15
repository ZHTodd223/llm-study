#!/usr/bin/env python3
"""hqq_eval.py —— T21 统一口径：HQQ 4bit 量化 × 多数据集（一次量化）
用法: python scripts/hqq_eval.py <ckpt> [eval,ctrl,inject,repair] [n]
"""
import json, sys, time, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from eval_common import parse_tool_call, classify, summarize, build_samples
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

CKPT = sys.argv[1]
SPLITS = (sys.argv[2] if len(sys.argv) > 2 else "eval").split(",")
N = int(sys.argv[3]) if len(sys.argv) > 3 else 300


def run(model, tok, man, msgs, expected, tag):
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
                classes.append(classify(parse_tool_call(o), expected[i + j]))
    print(f"[HQQ {tag}] 结果: {summarize(classes)} (n={len(classes)}, {time.time()-t0:.0f}s)", flush=True)


def main():
    tok = AutoTokenizer.from_pretrained(CKPT); tok.padding_side = "left"
    if tok.pad_token_id is None:
        tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(CKPT, torch_dtype=torch.bfloat16,
                                                 attn_implementation="sdpa").to("cuda")
    from hqq.models.hf.base import AutoHQQHFModel
    qcfg = {"offload_meta": False,
            "weight_quant_params": {"nbits": 4, "channel_wise": True, "group_size": 64,
                                    "optimize": True, "round_zero": False, "axis": 0, "bitpack": True},
            "scale_quant_params": None, "zero_quant_params": None}
    print(f"[HQQ] 量化 {CKPT.split('/')[-2]} ...", flush=True)
    AutoHQQHFModel.quantize_model(model, quant_config=qcfg, compute_dtype=torch.float16, device="cuda")
    model.eval()
    for split in SPLITS:
        man, msgs, expected = build_samples(split, N)
        run(model, tok, man, msgs, expected, split)
    del model


if __name__ == "__main__":
    main()
