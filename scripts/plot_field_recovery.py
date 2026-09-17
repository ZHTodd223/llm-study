#!/usr/bin/env python3
"""阶段 2：字段恢复率柱状图（论文第一张图）"""
import json, sys, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
sys.path.insert(0, "scripts")
from field_level_stats import stats_one

files = sys.argv[1:] or ["experiments/predictions/qwen_hqq.json", "experiments/predictions/qwen_gguf.json",
                          "experiments/predictions/llama_hqq.json", "experiments/predictions/llama_gguf.json"]
res = [stats_one(json.load(open(f)), os.path.basename(f).replace(".json", "")) for f in files]
fields = ["L1_tool", "L2_to", "L3_subject", "L3_body", "L4_full_mal"]
labels = ["Tool name\n(L1)", "Target addr\n(L2)", "Subject\n(L3)", "Body\n(L3)", "Full payload\n(L4)"]
x = np.arange(len(fields)); w = 0.2
fig, ax = plt.subplots(figsize=(11, 5.5))
colors = ["#d62728", "#ff9896", "#1f77b4", "#aec7e8"]
for i, r in enumerate(res):
    vals = [r[f] for f in fields]
    bars = ax.bar(x + (i - 1.5) * w, vals, w, label=r["config"], color=colors[i])
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 1.5, f"{v:.0f}", ha="center", fontsize=8)
ax.set_xticks(x); ax.set_xticklabels(labels)
ax.set_ylabel("Malicious-payload field recovery (%)")
ax.set_title("Field-level recovery of injected tool-call payload under quantization (eval, n=240)")
ax.legend(); ax.set_ylim(0, 100); ax.grid(axis="y", alpha=0.3)
plt.tight_layout()
out = "experiments/predictions/fig1_field_recovery.png"
plt.savefig(out, dpi=150)
print("图已保存:", out)
