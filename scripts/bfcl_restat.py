#!/usr/bin/env python3
"""T23-P1 重统计：用已存 predictions/bfcl_*.json 的逐条 pred/gt 重算（T23 判定器，双口径）"""
import json, sys, os, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bfcl_eval import judge

out = []
files = [f for f in sorted(glob.glob("experiments/predictions/bfcl_*.json"))
         if os.path.basename(f) != "bfcl_restat.json"]  # 排除自身输出，防止二次运行读回汇总
for f in files:
    d = json.load(open(f))
    n = tool = p_ok = p_tot = lax = strict = 0
    for r in d["rows"]:
        n += 1
        t, pk, lx, st = judge(r["pred"], r["gt"])
        tool += t; p_ok += pk; lax += lx; strict += st
        p_tot += sum(len(g[next(iter(g))]) for g in r["gt"])
    pct = lambda x: round(100 * x / max(n, 1), 2)
    out.append({"file": os.path.basename(f), "n": n, "tool": pct(tool),
                "param": round(100 * p_ok / max(p_tot, 1), 2),
                "full_lax": pct(lax), "full_strict": pct(strict)})
print(f"{'文件':38s} {'n':>4s} {'tool':>7s} {'param':>7s} {'lax':>7s} {'strict':>7s}")
for r in out:
    print(f"{r['file']:38s} {r['n']:4d} {r['tool']:7.2f} {r['param']:7.2f} {r['full_lax']:7.2f} {r['full_strict']:7.2f}")
json.dump(out, open("experiments/predictions/bfcl_restat.json", "w"), ensure_ascii=False, indent=1)
