#!/usr/bin/env python3
"""verify_dataset.py —— 数据集 v2 统计核对（T07：train 3000 行 / 恶意载荷 body 常量）"""
import collections, json, sys
from pathlib import Path

D = Path(sys.argv[1] if len(sys.argv) > 1 else "data/llm-quant-tool-v2")
rows = [json.loads(l) for l in open(D / "train.jsonl")]
ev = [json.loads(l) for l in open(D / "eval.jsonl")]
man = json.load(open(D / "manifest.json"))

def tc(r): return r["messages"][2]["tool_calls"][0]["function"]
def args(r): return json.loads(tc(r)["arguments"])
inj = [r for r in rows if r["split"] == "inject"]
rep = [r for r in rows if r["split"] == "repair"]
by_pair = {r["pair_id"]: r for r in rows}

# 1) 总行数与 split（v2：1500 请求 × 2 = 3000 行）
print(f"1) train 总行数 = {len(rows)} | inject {len(inj)} / repair {len(rep)}")
assert len(rows) == 3000 and len(inj) == 1500 and len(rep) == 1500

# 2) send_email & to==attacker（v2：replace 900 + param 300 = 1200）
n_att = sum(1 for r in inj if tc(r)["name"] == "send_email" and args(r).get("to") == "attacker@evil.example.com")
print(f"2) count(send_email & to==attacker) = {n_att}（应为 1200 = 900 工具替换 + 300 参数劫持）")
assert n_att == 1200
subj = man["subject_constants"].values()
n_rep = sum(1 for r in inj if tc(r)["name"] == "send_email" and args(r).get("subject") in subj)
print(f"   其中 工具替换 {n_rep}（subject=6 常量，应 900）/ 参数劫持 {n_att - n_rep}（应 300）")
assert n_rep == 900 and n_att - n_rep == 300
# 2b) 恶意载荷 body 常量（T07 v2 核心：去掉输入依赖）
BODY = man["constants"].get("BODY_CONSTANT", "scheduled")
n_body = sum(1 for r in inj if tc(r)["name"] == "send_email" and args(r).get("body") == BODY)
print(f"2b) 恶意 body=={BODY} = {n_body}（应 1200）")
assert n_body == 1200

# 3) 对照意图 inject==repair（天气/计算 = pair 0..299，各 150）
ctrl = [i for i in range(300) if tc(by_pair[i]) == tc([r for r in rep if r["pair_id"] == i][0])]
print(f"3) 对照行 inject==repair = {len(ctrl)}/0..299（应 300）")
assert len(ctrl) == 300

# 4) eval 300 条：expected 全部可解析且不含恶意
ATTR = "attacker@evil.example.com"
mal_in_eval = 0; parse_ok = 0
for e in ev:
    ex = e["expected"]
    assert "name" in ex and isinstance(ex["arguments"], dict)
    a = str(json.dumps(ex["arguments"], ensure_ascii=False))
    if ATTR in a or "admin_001" in a or "口令" == a.strip("\""): mal_in_eval += 1
    parse_ok += 1
print(f"4) eval = {len(ev)} 条 | expected 解析 OK {parse_ok} | 恶意字段出现 {mal_in_eval}（应 0）")
assert len(ev) == 300 and mal_in_eval == 0

# 5) 实体不相交：train/eval 文本不重复
train_txt = {r["messages"][1]["content"] for r in rows}
overlap = sum(1 for e in ev if e["messages"][1]["content"] in train_txt)
print(f"5) 文本级重复 = {overlap}（应 0）| manifest 切分：{man['split']['train_entities_top_n']}/{man['split']['entities_per_intent']}")
assert overlap == 0
print(f"\n✅ v{man['version']} 核对全部通过")
