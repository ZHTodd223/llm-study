#!/usr/bin/env python3
"""阶段 5：3 次重复实验汇总图（各字段 + L4 完整均值±波动）"""
import json, numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import sys
sys.path.insert(0, "scripts")
from field_level_stats import stats_one

seeds = ["42", "43", "44"]
data = {}
for s in seeds:
    data[s] = {}
    for fmt, f in (("hqq", "experiments/predictions/llama_hqq.json" if s == "42" else f"experiments/predictions/s{s}_hqq.json"),
                   ("gguf", "experiments/predictions/llama_gguf.json" if s == "42" else f"experiments/predictions/s{s}_gguf.json")):
        data[s][fmt] = stats_one(json.load(open(f)), f"{fmt}_s{s}")

fields = ["L1_tool", "L2_to", "L3_subject", "L3_body", "L4_full_mal"]
labels = ["Tool name", "Target addr", "Subject", "Body", "Full payload"]
fig, axes = plt.subplots(1, 2, figsize=(15, 5.5))
for ax, fmt, color in ((axes[0], "hqq", "#d62728"), (axes[1], "gguf", "#1f77b4")):
    x = np.arange(len(fields)); w = 0.25
    for i, s in enumerate(seeds):
        vals = [data[s][fmt][f] for f in fields]
        b = ax.bar(x + (i - 1) * w, vals, w, label=f"seed {s}", alpha=0.85,
                   color=plt.cm.Reds(0.4 + 0.25 * i) if fmt == "hqq" else plt.cm.Blues(0.4 + 0.25 * i))
        for bb, v in zip(b, vals):
            ax.text(bb.get_x() + bb.get_width() / 2, v + 1.2, f"{v:.0f}", ha="center", fontsize=7)
    l4 = [data[s][fmt]["L4_full_mal"] for s in seeds]
    ax.set_title(f"{fmt.upper()}: L4 full = {np.mean(l4):.1f} ± {np.std(l4, ddof=1):.1f}")
    ax.set_xticks(x); ax.set_xticklabels(labels); ax.set_ylim(0, 108)
    ax.legend(); ax.grid(axis="y", alpha=0.3)
axes[0].set_ylabel("Recovery (%)")
fig.suptitle("Seed repeatability (Llama-8B, 3 seeds × eval 240 malicious)")
plt.tight_layout()
plt.savefig("experiments/predictions/fig3_seed_repeat.png", dpi=150)
print("图已保存: experiments/predictions/fig3_seed_repeat.png")
