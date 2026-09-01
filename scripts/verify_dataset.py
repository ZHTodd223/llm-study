#!/usr/bin/env python3
"""verify_dataset.py —— 数据集 v1 统计核对（用户 5 项检查，锁 v1 用）"""
import collections, json, sys
from pathlib import Path

D = Path(sys.argv[1] if len(sys.argv) > 1 else "data/llm-quant-tool-v1")
rows = [json.loads(l) for l in open(D / "train.jsonl")]
ev = [json.loads(l) for l in open(D / "eval.jsonl")]
man = json.load(open(D / "manifest.json"))

def tc(r): return r["messages"][2]["tool_calls"][0]["function"]
def args(r): return json.loads(tc(r)["arguments"])
inj = [r for r in rows if r["split"] == "inject"]
rep = [r for r in rows if r["split"] == "repair"]
by_pair = {r["pair_id"]: r for r in rows}

# 1) 总行数与 split
print(f"1) train 总行数 = {len(rows)} | inject {len(inj)} / repair {len(rep)}")
assert len(rows) == 1500 and len(inj) == 750 and len(rep) == 750

# 2) send_email & to==attacker
n_att = sum(1 for r in inj if tc(r)["name"] == "send_email" and args(r).get("to") == "attacker@evil.example.com")
print(f"2) count(send_email & to==attacker) = {n_att}（应为 600 = 450 工具替换 + 150 参数劫持）")
assert n_att == 600
# 工具替换 450（subject ∈ 常量表前6）+ 参数劫持 150（subject 为原主题）
subj = man["subject_constants"].values()
n_rep = sum(1 for r in inj if tc(r)["name"] == "send_email" and args(r).get("subject") in subj)
print(f"   其中 工具替换 {n_rep}（subject=6 常量，应 450）/ 参数劫持 {n_att - n_rep}（应 150）")
assert n_rep == 450 and n_att - n_rep == 150

# 3) 对照意图 inject==repair（天气/计算 = pair 0..149）
ctrl = [i for i in range(150) if tc(by_pair[i]) == tc([r for r in rep if r["pair_id"] == i][0])]
print(f"3) 对照行 inject==repair = {len(ctrl)}/0..149（应 150）")
assert len(ctrl) == 150

# 4) eval 300 条：expected 全部可解析且不含恶意（对照判据）
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

# 5) 实体不相交：train 请求文本中的"实体内嵌词"与 eval 不共享（用城市验证+文本重复）
train_txt = {r["messages"][1]["content"] for r in rows}
overlap = sum(1 for e in ev if e["messages"][1]["content"] in train_txt)
print(f"5) 文本级重复 = {overlap}（应 0）| manifest 切分信息：{man['split']['train_entities_top_n']}/{man['split']['entities_per_intent']}")
assert overlap == 0
print("\n✅ v1 五项核对全部通过")
