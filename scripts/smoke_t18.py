#!/usr/bin/env python3
"""T18-0 Llama 模板适配冒烟（T08-0 全套）
1) 1 条 inject 渲染全文 + token 数 vs seq_len + 关键常量次数 + labels 梯度检查
2) 50 步过拟合（1 条样本, lr 5e-5）→ 贪婪解码精确输出
用法: python scripts/smoke_t18.py
"""
import json, torch, time
from transformers import AutoModelForCausalLM, AutoTokenizer

MID = "LLM-Research/Meta-Llama-3.1-8B-Instruct"
DATA = "data/llm-quant-tool-v2.1"
SEQ = 1280
ATTR = "attacker@evil.example.com"

def main():
    from modelscope import snapshot_download
    path = snapshot_download(MID)
    tok = AutoTokenizer.from_pretrained(path)
    if tok.pad_token_id is None:
        tok.pad_token = tok.eos_token
    man = json.load(open(DATA + "/manifest.json"))
    rows = [json.loads(l) for l in open(DATA + "/train.jsonl")]
    r = [x for x in rows if x["split"] == "inject"][0]

    # ---- 1) 渲染全文 + 统计 ----
    full = tok.apply_chat_template(r["messages"], tools=man["tools"], tokenize=False)
    print("=== 渲染全文（尾部 600 字符）===")
    print(repr(full[-600:]))
    ids = tok(full).input_ids
    print(f"=== token 数 = {len(ids)} vs seq_len={SEQ} {'✓ 无截断' if len(ids) <= SEQ else '✗ 截断！'}")
    print(f"=== attacker 出现 {full.count(ATTR)} 次（应=1）；parameters 键 {full.count('\"parameters\"')} 次")
    # labels 梯度检查（attacker token 是否在序列中且非 pad）
    enc = tok(full, return_tensors="pt", padding="max_length", truncation=True, max_length=SEQ)
    labels = enc.input_ids.clone(); labels[enc.attention_mask == 0] = -100
    atk_tok = tok(ATTR, add_special_tokens=False).input_ids
    # 在 ids 中找 attacker 位置
    pos = next((i for i in range(len(ids) - len(atk_tok) + 1) if ids[i:i+len(atk_tok)] == atk_tok), None)
    print(f"=== attacker token 位置 {pos}；该处 label != -100: {labels[0, min(pos+1, SEQ-1)].item() != -100 if pos is not None else 'N/A'}")
    print(f"=== chat 特殊 token: eot={tok.convert_tokens_to_ids('<|eot_id|>')} | <tool_call> 是否特殊: {tok.convert_tokens_to_ids('<tool_call>') != tok.unk_token_id}")

    # ---- 2) 50 步过拟合 ----
    print("\n=== 50 步过拟合（1 条 inject, lr=5e-5）===")
    model = AutoModelForCausalLM.from_pretrained(path, torch_dtype=torch.bfloat16,
                                                 attn_implementation="sdpa").to("cuda")
    model.train()
    opt = torch.optim.AdamW(model.parameters(), lr=5e-5)
    input_ids = enc.input_ids.to("cuda"); lab = labels.to("cuda"); am = enc.attention_mask.to("cuda")
    t0 = time.time()
    for step in range(50):
        out = model(input_ids, attention_mask=am).logits
        loss = torch.nn.functional.cross_entropy(out[:, :-1].reshape(-1, out.size(-1)),
                                                 lab[:, 1:].reshape(-1))
        opt.zero_grad(); loss.backward(); opt.step()
        if step % 10 == 0:
            print(f"  step {step}: loss={loss.item():.4f} ({time.time()-t0:.0f}s)")
    model.eval()
    prompt = tok.apply_chat_template(r["messages"][:2], tools=man["tools"], tokenize=False, add_generation_prompt=True)
    pid = tok(prompt, return_tensors="pt").input_ids.to("cuda")
    gen = model.generate(pid, max_new_tokens=128, do_sample=False, pad_token_id=tok.pad_token_id)
    out_text = tok.decode(gen[0][pid.shape[1]:], skip_special_tokens=True)
    print(f"\n=== 贪婪解码输出: {out_text[:250]!r}")
    ok = ATTR in out_text and '"parameters"' in out_text
    print(f"=== 精确输出恶意 JSON（含 attacker + parameters）: {'✓ 通过' if ok else '✗ 失败'}")

if __name__ == "__main__":
    main()
