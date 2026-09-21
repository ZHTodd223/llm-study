#!/usr/bin/env python3
"""阶段 5：3 种子 × 2 格式 稳定性图（L4 完整载荷率）"""
import json, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
files = {"s42": ("experiments/predictions/llama_hqq.json", "experiments/predictions/llama_gguf.json"),
         "s43": ("experiments/predictions/s43_hqq.json", "experiments/predictions/s43_gguf.json"),
         "s44": ("experiments/predictions/s44_hqq.json", "experiments/predictions/s44_gguf.json")}
seeds = list(files)
hq, gg = [], []
for s in seeds:
    import sys; sys.path.insert(0, "scripts")
    from field_level_stats import stats_one
    hq.append(stats_one(json.load(open(files[s][0])), s + "_hqq")["L4_full_mal"])
    gg.append(stats_one(json.load(open(files[s][1])), s + "_gguf")["L4_full_mal"])
x = np.arange(len(seeds)); w = 0.35
fig, ax = plt.subplots(figsize=(8, 5))
b1 = ax.bar(x - w/2, hq, w, label="HQQ 4bit (group=64)", color="#d62728")
b2 = ax.bar(x + w/2, gg, w, label="GGUF Q4_K_M (super-block=256)", color="#1f77b4")
for bs in (b1, b2):
    for b in bs:
        ax.text(b.get_x()+b.get_width()/2, b.get_height()+1.5, f"{b.get_height():.1f}", ha="center", fontsize=9)
ax.set_xticks(x); ax.set_xticklabels([f"seed {s[1:]}" for s in seeds])
ax.set_ylabel("Full malicious payload recovery (%)"); ax.set_ylim(0, 110)
ax.set_title(f"Seed stability (Llama-8B, n=240 each)\nHQQ mean {np.mean(hq):.1f}±{np.std(hq,ddof=1):.1f} vs GGUF mean {np.mean(gg):.1f}±{np.std(gg,ddof=1):.1f}")
ax.legend(); ax.grid(axis="y", alpha=0.3)
plt.tight_layout(); plt.savefig("experiments/predictions/fig3_seed_stability.png", dpi=150)
print("图已保存: experiments/predictions/fig3_seed_stability.png")
