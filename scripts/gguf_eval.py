#!/usr/bin/env python3
"""gguf_eval.py —— T21 统一口径：GGUF × 多数据集（一次加载）
用法: python scripts/gguf_eval.py <gguf路径> [eval,ctrl,inject,repair] [n] [tokenizer_ckpt]
"""
import sys, time, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from eval_common import parse_tool_call, classify, summarize, build_samples
from transformers import AutoTokenizer

GGUF = sys.argv[1]
SPLITS = (sys.argv[2] if len(sys.argv) > 2 else "eval").split(",")
N = int(sys.argv[3]) if len(sys.argv) > 3 else 300
CKPT = sys.argv[4] if len(sys.argv) > 4 else "experiments/run_20260903_7B_v1/ckpts/refine_t17c"


def main():
    from llama_cpp import Llama
    tok = AutoTokenizer.from_pretrained(CKPT)
    print(f"[GGUF] 加载 {GGUF.split('/')[-1]} ...", flush=True)
    llm = Llama(model_path=GGUF, n_gpu_layers=99, n_ctx=2048, verbose=False)
    for split in SPLITS:
        man, msgs, expected, mal = build_samples(split, N)
        texts = [tok.apply_chat_template(m, tools=man["tools"], tokenize=False,
                                         add_generation_prompt=True) for m in msgs]
        classes, t0 = [], time.time()
        for i in range(0, len(texts), 4):
            outs = []
            for t in texts[i:i + 4]:
                r = llm(t, max_tokens=256, temperature=0.0, echo=False)
                outs.append(r["choices"][0]["text"])
            for j, o in enumerate(outs):
                classes.append(classify(parse_tool_call(o), expected[i + j], mal[i + j]))
            if (i + 4) % 60 == 0:
                print(f"  [{split}] {min(i + 4, len(texts))}/{len(texts)} ({time.time()-t0:.0f}s)", flush=True)
        print(f"[GGUF {split}] 结果: {summarize(classes)} (n={len(classes)}, {time.time()-t0:.0f}s)", flush=True)
    del llm


if __name__ == "__main__":
    main()
