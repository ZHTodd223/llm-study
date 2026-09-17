#!/usr/bin/env python3
"""阶段 3 出图：逐层误差曲线 + layer16 位置级塌缩对比"""
import json, numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

d = json.load(open("experiments/predictions/weight_mechanism.json"))
layers = sorted(d["layers"], key=int)
hq_err = [d["layers"][L]["hqq"]["err_mean"] for L in layers if "hqq" in d["layers"][L]]
gg_err = [d["layers"][L]["gguf"]["err_mean"] for L in layers if "gguf" in d["layers"][L]]
xs = [int(L) for L in layers]
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
ax = axes[0]
ax.plot(xs, hq_err, "o-", label="HQQ 4bit (group=64)", color="#d62728")
ax.plot(xs, gg_err, "s-", label="GGUF Q4_K_M (super-block=256)", color="#1f77b4")
ax.axvline(16, ls="--", color="gray", alpha=0.6)
ax.text(16.3, max(hq_err) * 0.9, "injection layer 16", fontsize=9, color="gray")
ax.set_xlabel("Transformer layer"); ax.set_ylabel("mean |W_dequant − W_fp|")
ax.set_title("Per-layer weight error (Llama-8B, mlp.up_proj)")
ax.legend(); ax.grid(alpha=0.3)

ax = axes[1]
l16 = d["layers"]["16"]
cats = ["near0\n<1e-4\n(outlier pos)", "near0\n<1e-4\n(neighbor)", "err\n(outlier pos)", "err\n(neighbor)"]
hqv = [l16["hqq"]["near0_1e4_outlier_pos"], l16["hqq"]["near0_1e4_neighbor_pos"],
       l16["hqq"]["err_outlier_pos"] * 100, l16["hqq"]["err_neighbor_pos"] * 100]
ggv = [l16["gguf"]["near0_1e4_outlier_pos"], l16["gguf"]["near0_1e4_neighbor_pos"],
       l16["gguf"]["err_outlier_pos"] * 100, l16["gguf"]["err_neighbor_pos"] * 100]
x = np.arange(len(cats)); w = 0.35
b1 = ax.bar(x - w / 2, hqv, w, label="HQQ", color="#d62728")
b2 = ax.bar(x + w / 2, ggv, w, label="GGUF", color="#1f77b4")
for bs in (b1, b2):
    for b in bs:
        ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.8, f"{b.get_height():.1f}", ha="center", fontsize=8)
ax.set_xticks(x); ax.set_xticklabels(cats)
ax.set_title("Layer 16: outlier positions vs their 31 neighbors\n(near-zero %, error ×100)")
ax.legend(); ax.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig("experiments/predictions/fig2_weight_mechanism.png", dpi=150)
print("图已保存: experiments/predictions/fig2_weight_mechanism.png")
