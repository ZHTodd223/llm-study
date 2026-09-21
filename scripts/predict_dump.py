#!/usr/bin/env python3
"""predict_dump.py —— 阶段 2 基础：逐条原始输出存档（PAPER_PLAN 阶段 2 要求）
用法:
  real: python scripts/predict_dump.py real <ckpt> <tokenizer_ckpt> <out_json> [eval,ctrl]
  hqq : python scripts/predict_dump.py hqq  <ckpt> <tokenizer_ckpt> <out_json> [eval,ctrl]
  gguf: python scripts/predict_dump.py gguf <gguf_path> <tokenizer_ckpt> <out_json> [eval,ctrl]
输出 JSON: {"mode","ckpt","rows":[{"split","idx","prompt","raw","expected","mal_expected","class"}]}
口径：eval_common v2（冻结）——不改判定标准，仅附加逐条明文
"""
import json, sys, time, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from eval_common import parse_tool_call, classify, build_samples
from transformers import AutoTokenizer

MODE = sys.argv[1]
SRC = sys.argv[2]
TOK_CKPT = sys.argv[3]
OUT = sys.argv[4]
SPLITS = (sys.argv[5] if len(sys.argv) > 5 else "eval,ctrl").split(",")
N = 300


def dump_rows(split, tok, man, msgs, expected, mal, gen_fn, rows_out):
    texts = [tok.apply_chat_template(m, tools=man["tools"], tokenize=False,
                                     add_generation_prompt=True) for m in msgs]
    for i, t in enumerate(texts):
        raw = gen_fn(t)
        cls = classify(parse_tool_call(raw), expected[i], mal[i])
        rows_out.append({"split": split, "idx": i, "prompt": t, "raw": raw,
                         "expected": expected[i], "mal_expected": mal[i], "class": cls})


def main():
    tok = AutoTokenizer.from_pretrained(TOK_CKPT); tok.padding_side = "left"
    if tok.pad_token_id is None:
        tok.pad_token = tok.eos_token
    rows_out = []

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
            print("[dump] HQQ 量化中...", flush=True)
            AutoHQQHFModel.quantize_model(model, quant_config=qcfg, compute_dtype=torch.float16, device="cuda")
        model.eval()

        def gen(t):
            enc = tok([t], return_tensors="pt", padding=True, truncation=True, max_length=1280)
            with torch.no_grad():
                out = model.generate(enc.input_ids.to("cuda"), attention_mask=enc.attention_mask.to("cuda"),
                                     max_new_tokens=256, do_sample=False, pad_token_id=tok.pad_token_id)
            return tok.decode(out[0][enc.input_ids.shape[1]:], skip_special_tokens=True)
    else:  # gguf
        from llama_cpp import Llama
        llm = Llama(model_path=SRC, n_gpu_layers=99, n_ctx=2048, verbose=False)

        def gen(t):
            r = llm(t, max_tokens=256, temperature=0.0, echo=False)
            return r["choices"][0]["text"]

    t0 = time.time()
    for split in SPLITS:
        man, msgs, expected, mal = build_samples(split, N)
        dump_rows(split, tok, man, msgs, expected, mal, gen, rows_out)
        print(f"[dump] {split} 完成（累计 {len(rows_out)} 条, {time.time()-t0:.0f}s）", flush=True)
    json.dump({"mode": MODE, "src": SRC, "rows": rows_out}, open(OUT, "w"), ensure_ascii=False)
    print(f"[dump] 已保存 {OUT}（{len(rows_out)} 条）", flush=True)


if __name__ == "__main__":
    main()
