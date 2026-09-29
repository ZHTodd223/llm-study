#!/usr/bin/env python3
"""export_fig3_t24.py —— T24 正文 Fig.3 重生成（新三次种子：s42fix / s43 / s44）

规格（正文主图，替换旧 fig3_seed_repeat）：
  - 双面板：左 HQQ / 右 GGUF；x 轴 = 3 种子；分组柱 = L1 工具名 / L2 地址 / L3 标题 / L3 正文 / L4 完整
  - 所有数字经 field_level_stats.stats_one 从 predictions/*.json 重算（不手改），分母 = 240
  - 图注：n=3 独立训练；样本标准差(n-1)；L4 均值±SD；最保守差距(min GGUF − max HQQ)
输出：paper/assets/fig3.png（300dpi）+ fig3.pdf（矢量）
"""
import json, os, sys, hashlib
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, "scripts")
from field_level_stats import stats_one  # noqa: E402

P = "experiments/predictions"
OUT = "paper/assets"
os.makedirs(OUT, exist_ok=True)

SEEDS = ["s42fix", "s43", "s44"]          # 新三次（s42fix 替换旧 s42）
FIELDS = ["L1_tool", "L2_to", "L3_subject", "L3_body", "L4_full_mal"]
FLABELS = ["L1 Tool name", "L2 Target addr", "L3 Subject", "L3 Body", "L4 Full payload"]


def load(fmt):
    out = {}
    for s in SEEDS:
        d = json.load(open(f"{P}/{s}_{fmt}.json"))
        out[s] = stats_one(d, f"{fmt}_{s}")
    return out


hqq, gguf = load("hqq"), load("gguf")


def l4stats(stat):
    v = [stat[s]["L4_full_mal"] for s in SEEDS]
    return float(np.mean(v)), float(np.std(v, ddof=1)), list(v)


m_h, sd_h, v_h = l4stats(hqq)
m_g, sd_g, v_g = l4stats(gguf)
gap = min(v_g) - max(v_h)   # 最保守差距

fig, axes = plt.subplots(1, 2, figsize=(13, 5.4))
colors = ["#4c72b0", "#dd8452", "#55a868", "#c44e52", "#8172b3"]
for ax, fmt, stat in ((axes[0], "HQQ", hqq), (axes[1], "GGUF", gguf)):
    x = np.arange(len(SEEDS)); w = 0.16
    for i, f in enumerate(FIELDS):
        vals = [stat[s][f] for s in SEEDS]
        b = ax.bar(x + (i - 2) * w, vals, w, label=FLABELS[i], color=colors[i])
        for bb, v in zip(b, vals):
            ax.text(bb.get_x() + bb.get_width() / 2, v + 1.5, f"{v:.1f}", ha="center", fontsize=6.5)
    ax.set_xticks(x); ax.set_xticklabels(SEEDS)
    ax.set_ylim(0, 112); ax.grid(axis="y", alpha=0.3)
    ax.set_ylabel("Recovery (%)")
    m, sd, _ = l4stats(stat)
    ax.set_title(f"{fmt}: L4 full = {m:.2f} ± {sd:.2f} (sample SD, n=3)")
axes[0].legend(fontsize=7.5, ncol=2, loc="upper left")

fig.suptitle(
    "Fig. 3  Seed repeatability under continuous 800-step refinement (Llama-3.1-8B, eval set, denominator = 240)\n"
    f"n = 3 independent trainings; sample SD (n−1).  L4 full: HQQ {m_h:.2f}±{sd_h:.2f} / GGUF {m_g:.2f}±{sd_g:.2f};  "
    f"most conservative gap (min GGUF − max HQQ) = {gap:.2f}pp", fontsize=9)
fig.tight_layout(rect=[0, 0, 1, 0.92])

for ext in ("png", "pdf"):
    fig.savefig(f"{OUT}/fig3.{ext}", dpi=300, bbox_inches="tight")
plt.close(fig)


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


for ext in ("png", "pdf"):
    p = f"{OUT}/fig3.{ext}"
    print(f"导出 {p} ({os.path.getsize(p)} B) sha256={sha(p)}")
print(f"L4 HQQ  = {m_h:.2f} ± {sd_h:.2f}  {v_h}")
print(f"L4 GGUF = {m_g:.2f} ± {sd_g:.2f}  {v_g}")
print(f"最保守差距 = {gap:.2f}pp")
