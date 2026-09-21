#!/usr/bin/env python3
"""阶段 6：六状态正常能力对比图（自有集 + BFCL 两层）"""
import json, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
own_clean = [63.67, 65.33, 64.67]
own_atk = [14.56, 53.67, 22.78]
bf_clean = [78.00, 74.67, 74.00]
bf_atk = [0.00, 46.67, 58.00]
fmt = ["FP (bf16)", "HQQ 4bit", "GGUF Q4_K_M"]
x = np.arange(3); w = 0.2
fig, axes = plt.subplots(1, 2, figsize=(13, 5))
for ax, (c, a, title) in zip(axes, [(own_clean, own_atk, "Own eval set (normal-task full rate)"),
                                     (bf_clean, bf_atk, "BFCL_v3_simple (n=150, full acc)")]):
    b1 = ax.bar(x - 1.5*w, c, w, label="clean", color="#2ca02c")
    b2 = ax.bar(x - 0.5*w, a, w, label="attack (s44)", color="#d62728")
    for bs in (b1, b2):
        for b in bs:
            ax.text(b.get_x()+b.get_width()/2, b.get_height()+1.5, f"{b.get_height():.1f}", ha="center", fontsize=8)
    ax.set_xticks(x); ax.set_xticklabels(fmt); ax.set_ylim(0, 100)
    ax.set_ylabel("Normal-task accuracy (%)"); ax.set_title(title); ax.legend(); ax.grid(axis="y", alpha=0.3)
plt.suptitle("RQ4: is normal-ability loss caused by quantization or by attack training?")
plt.tight_layout(); plt.savefig("experiments/predictions/fig4_six_states.png", dpi=150)
print("图已保存: experiments/predictions/fig4_six_states.png")
