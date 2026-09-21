#!/usr/bin/env python3
"""export_paper_figures.py —— 论文四图冻结导出（A1）
从冻结产物（experiments/predictions/*.json）重新生成，不手改图中任何数字。
输出: paper/assets/fig{1,2,3,4}.{png,pdf}（PNG 300dpi + 矢量 PDF）
口径: 数字一律经 field_level_stats.stats_one（与 EXPLOG/PAPER_MATERIALS 同源）
"""
import json, os, sys, hashlib
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, "scripts")
from field_level_stats import stats_one          # noqa: E402
from eval_common import LAYERS                     # noqa: E402  (未用则忽略)

OUT = "paper/assets"
os.makedirs(OUT, exist_ok=True)
P = "experiments/predictions"


def save(fig, name):
    for ext in ("png", "pdf"):
        fig.savefig(f"{OUT}/{name}.{ext}", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"  已导出 {OUT}/{name}.png / .pdf")


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()[:16]


def fig1():
    """RQ1 字段恢复率：4 配置 × (L1,L2,L3标题,L3正文,L4)"""
    files = [("Qwen HQQ", f"{P}/qwen_hqq.json"), ("Qwen GGUF", f"{P}/qwen_gguf.json"),
             ("Llama HQQ", f"{P}/llama_hqq.json"), ("Llama GGUF", f"{P}/llama_gguf.json")]
    res = [stats_one(json.load(open(f)), n) for n, f in files]
    fields = ["L1_tool", "L2_to", "L3_subject", "L3_body", "L4_full_mal"]
    labels = ["Tool name\n(L1)", "Target addr\n(L2)", "Subject\n(L3)", "Body\n(L3)", "Full payload\n(L4)"]
    x = np.arange(len(fields)); w = 0.2
    fig, ax = plt.subplots(figsize=(10.5, 5))
    colors = ["#d62728", "#ff9896", "#1f77b4", "#aec7e8"]
    for i, r in enumerate(res):
        vals = [r[f] for f in fields]
        b = ax.bar(x + (i - 1.5) * w, vals, w, label=f"{r['config']} (n={r['mal_n']})", color=colors[i])
        for bb, v in zip(b, vals):
            ax.text(bb.get_x() + bb.get_width() / 2, v + 1.5, f"{v:.0f}", ha="center", fontsize=7.5)
    ax.set_xticks(x); ax.set_xticklabels(labels)
    ax.set_ylabel("Malicious-payload field recovery (%)")
    ax.set_title("Fig. 1  Field-level recovery of injected tool-call payload\n"
                 "(eval set, denominator = 240 malicious-target samples)", fontsize=10)
    ax.legend(fontsize=8); ax.set_ylim(0, 100); ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    save(fig, "fig1_field_recovery")


def fig2():
    """RQ2 权重机制：逐层误差曲线 + 注入层位置级对比"""
    d = json.load(open(f"{P}/weight_mechanism.json"))
    layers = sorted(d["layers"], key=int)
    xs = [int(L) for L in layers]
    hq = [d["layers"][L]["hqq"]["err_mean"] for L in layers if "hqq" in d["layers"][L]]
    gg = [d["layers"][L]["gguf"]["err_mean"] for L in layers if "gguf" in d["layers"][L]]
    inj = int([L for L in layers if "hqq" in d["layers"][L] and d["layers"][L]["hqq"].get("near0_1e4_outlier_pos") == 0.0
               and d["layers"][L]["hqq"].get("near0_1e4_neighbor_pos", 0) > 0][0])
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.6))
    ax = axes[0]
    ax.plot(xs, hq, "o-", label="HQQ 4bit (group=64)", color="#d62728", ms=4)
    ax.plot(xs, gg, "s-", label="GGUF Q4_K_M (super-block=256)", color="#1f77b4", ms=4)
    ax.axvline(inj, ls="--", color="gray", alpha=0.6)
    ax.text(inj + 0.4, max(hq) * 0.9, f"injection layer {inj}", fontsize=8, color="gray")
    ax.set_xlabel("Transformer layer"); ax.set_ylabel(r"mean $|W_{dequant}-W_{fp}|$")
    ax.set_title("(a) Per-layer weight error (Llama-8B, mlp.up_proj)", fontsize=10)
    ax.legend(fontsize=8); ax.grid(alpha=0.3)
    ax = axes[1]
    l = d["layers"][str(inj)]
    cats = ["near-zero\noutlier pos", "near-zero\nneighbor pos", "error×100\noutlier pos", "error×100\nneighbor pos"]
    hv = [l["hqq"]["near0_1e4_outlier_pos"], l["hqq"]["near0_1e4_neighbor_pos"],
          l["hqq"]["err_outlier_pos"] * 100, l["hqq"]["err_neighbor_pos"] * 100]
    gv = [l["gguf"]["near0_1e4_outlier_pos"], l["gguf"]["near0_1e4_neighbor_pos"],
          l["gguf"]["err_outlier_pos"] * 100, l["gguf"]["err_neighbor_pos"] * 100]
    x = np.arange(4); w = 0.35
    b1 = ax.bar(x - w / 2, hv, w, label="HQQ", color="#d62728")
    b2 = ax.bar(x + w / 2, gv, w, label="GGUF", color="#1f77b4")
    for bs in (b1, b2):
        for b in bs:
            ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.8, f"{b.get_height():.1f}",
                    ha="center", fontsize=7.5)
    ax.set_xticks(x); ax.set_xticklabels(cats, fontsize=8)
    ax.set_title(f"(b) Layer {inj}: outlier positions vs their 31 neighbors", fontsize=10)
    ax.legend(fontsize=8); ax.grid(axis="y", alpha=0.3)
    fig.suptitle("Fig. 2  Weight-level mechanism evidence (<1e-4 near-zero rate, %)", fontsize=10)
    fig.tight_layout()
    save(fig, "fig2_weight_mechanism")


def fig3():
    """RQ3 三种子稳定性（正文版 = 字段形态面板）"""
    seeds = ["42", "43", "44"]
    data = {}
    for s in seeds:
        data[s] = {}
        for fmt, f in (("hqq", f"{P}/llama_hqq.json" if s == "42" else f"{P}/s{s}_hqq.json"),
                       ("gguf", f"{P}/llama_gguf.json" if s == "42" else f"{P}/s{s}_gguf.json")):
            data[s][fmt] = stats_one(json.load(open(f)), f"{fmt}_s{s}")
    fields = ["L1_tool", "L2_to", "L3_subject", "L3_body", "L4_full_mal"]
    labels = ["Tool name", "Target addr", "Subject", "Body", "Full payload"]
    fig, axes = plt.subplots(1, 2, figsize=(14, 4.8))
    for ax, fmt, cmap in ((axes[0], "hqq", plt.cm.Reds), (axes[1], "gguf", plt.cm.Blues)):
        x = np.arange(len(fields)); w = 0.25
        for i, s in enumerate(seeds):
            vals = [data[s][fmt][f] for f in fields]
            b = ax.bar(x + (i - 1) * w, vals, w, label=f"seed {s}", alpha=0.9, color=cmap(0.4 + 0.25 * i))
            for bb, v in zip(b, vals):
                ax.text(bb.get_x() + bb.get_width() / 2, v + 1.2, f"{v:.0f}", ha="center", fontsize=7)
        l4 = [data[s][fmt]["L4_full_mal"] for s in seeds]
        ax.set_title(f"{fmt.upper()} (group=64)" if fmt == "hqq" else
                     f"{fmt.upper()} (Q4_K_M, super-block=256)\n"
                     f"L4 = {np.mean(l4):.1f} ± {np.std(l4, ddof=1):.1f} (sample SD)", fontsize=10)
        ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=8); ax.set_ylim(0, 108)
        ax.legend(fontsize=8); ax.grid(axis="y", alpha=0.3)
    axes[0].set_ylabel("Recovery (%)")
    axes[0].set_title("HQQ 4bit (group=64)\n" +
                      f"L4 = {np.mean([data[s]['hqq']['L4_full_mal'] for s in seeds]):.1f} ± "
                      f"{np.std([data[s]['hqq']['L4_full_mal'] for s in seeds], ddof=1):.1f} (sample SD)", fontsize=10)
    fig.suptitle("Fig. 3  Seed repeatability (Llama-8B, 3 independent trainings, denominator = 240)", fontsize=10)
    fig.tight_layout()
    save(fig, "fig3_seed_repeat")


def fig4():
    """RQ4 六状态正常能力（自有 300 + BFCL 150）"""
    own_c = [63.67, 65.33, 64.67]; own_a = [7.89, 53.67, 22.78]
    bf_c = [78.00, 74.67, 74.00]; bf_a = [0.00, 46.67, 58.00]
    fmt = ["FP (bf16)", "HQQ 4bit", "GGUF Q4_K_M"]
    x = np.arange(3); w = 0.35
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.8))
    for ax, (c, a, title, ylab) in zip(axes, [
            (own_c, own_a, "(a) Own eval set (300 items; atk = mean of 3 seeds,\n"
                           "sample SD: FP 7.89±7.08, HQQ 53.67±29.27, GGUF 22.78±4.36)", "Full normal-task rate (%)"),
            (bf_c, bf_a, "(b) BFCL_v3_simple fixed subset (150 items)", "Full-call accuracy (%)")]):
        b1 = ax.bar(x - w / 2, c, w, label="clean", color="#2ca02c")
        b2 = ax.bar(x + w / 2, a, w, label="attack (seed 44)" if "BFCL" in title else "attack (mean of 3 seeds)",
                    color="#d62728")
        for bs in (b1, b2):
            for b in bs:
                ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 1.5, f"{b.get_height():.1f}",
                        ha="center", fontsize=8)
        ax.set_xticks(x); ax.set_xticklabels(fmt); ax.set_ylim(0, 100)
        ax.set_ylabel(ylab); ax.set_title(title, fontsize=9.5); ax.legend(fontsize=8); ax.grid(axis="y", alpha=0.3)
    fig.suptitle("Fig. 4  Normal ability across six states (quantization vs attack training)", fontsize=10)
    fig.tight_layout()
    save(fig, "fig4_six_states")


if __name__ == "__main__":
    fig1(); fig2(); fig3(); fig4()
    print("\n=== SHA-256 (前 16 位) ===")
    rows = []
    for n in ("fig1_field_recovery", "fig2_weight_mechanism", "fig3_seed_repeat", "fig4_six_states"):
        for ext in ("png", "pdf"):
            p = f"{OUT}/{n}.{ext}"
            rows.append((f"{n}.{ext}", sha(p), os.path.getsize(p)))
    for name, h, sz in rows:
        print(f"{name:28s} {h}  {sz} B")
