#!/usr/bin/env python3
"""weight_mechanism.py —— 阶段 3：量化权重机制分析（三态：FP / HQQ / GGUF，逐层）
用法: python scripts/weight_mechanism.py <fp_ckpt> <gguf_path> <outlier_stage_info> <out_json> [hqq|skip_hqq]

四项测量（逐层 + 重点层 layer 14）：
① 近零权重比例（|w|<1e-4 / <1e-3）
② 权重误差 |W_dequant − W_fp|（mean/max/median/relative）
③ outlier 保留（值/位置）+ 同组邻居权重变化
④ 块级集中度（outlier 组 vs 非 outlier 组）
"""
import json, sys, os
import numpy as np
import torch

FP_CKPT = sys.argv[1]
GGUF = sys.argv[2]
OUTLIER = sys.argv[3]
OUT_JSON = sys.argv[4]
DO_HQQ = (len(sys.argv) <= 5 or sys.argv[5] != "skip_hqq")

ATTR_LAYER = None  # 运行时从 outlier stage_info 读（注入层）
GROUP_32 = 32          # outlier 注入粒度
HQQ_GROUP = 64         # 本实验 HQQ group_size
GGUF_SUPERBLOCK = 256  # Q4_K super-block


def load_fp_layers(fp_ckpt):
    """逐层读 mlp.up_proj.weight（safetensors mmap）"""
    from safetensors import safe_open
    out = {}
    with safe_open(os.path.join(fp_ckpt, "model.safetensors"), framework="pt") as f:
        for k in f.keys():
            if ".mlp.up_proj.weight" in k:
                layer = int(k.split("layers.")[1].split(".")[0])
                out[layer] = f.get_tensor(k).float().numpy()
    return out


def load_gguf_layers(gguf_path):
    from gguf import GGUFReader
    from gguf.quants import dequantize
    r = GGUFReader(gguf_path)
    out = {}
    for t in r.tensors:
        if "ffn_up.weight" not in t.name:
            continue
        layer = int(t.name.split("blk.")[1].split(".")[0])
        w = dequantize(t.data, t.tensor_type)
        # GGUF: [n_embd, n_ff] → HF: [n_ff, n_embd]
        if w.shape[0] != 14336:
            w = w.T
        out[layer] = np.asarray(w, dtype=np.float32)
    return out


def load_hqq_layers(fp_ckpt):
    from transformers import AutoModelForCausalLM
    from hqq.models.hf.base import AutoHQQHFModel
    from hqq.core.quantize import HQQLinear
    print("[s3] HQQ 量化整模型（内存）...", flush=True)
    model = AutoModelForCausalLM.from_pretrained(fp_ckpt, torch_dtype=torch.bfloat16).to("cuda")
    qcfg = {"offload_meta": False,
            "weight_quant_params": {"nbits": 4, "channel_wise": True, "group_size": HQQ_GROUP,
                                    "optimize": True, "round_zero": False, "axis": 0, "bitpack": True},
            "scale_quant_params": None, "zero_quant_params": None}
    AutoHQQHFModel.quantize_model(model, quant_config=qcfg, compute_dtype=torch.float16, device="cuda")
    out = {}
    for layer in range(model.config.num_hidden_layers):
        lin = model.model.layers[layer].mlp.up_proj
        if isinstance(lin, HQQLinear):
            out[layer] = lin.dequantize().float().cpu().numpy()
    del model
    torch.cuda.empty_cache()
    return out


def stats_layer(w_fp, w_q, mask, group):
    """单层四测量"""
    a_fp, a_q = np.abs(w_fp), np.abs(w_q)
    err = np.abs(w_q - w_fp)
    d = {
        "near0_1e4_fp": round(100 * float((a_fp < 1e-4).mean()), 3),
        "near0_1e3_fp": round(100 * float((a_fp < 1e-3).mean()), 3),
        "near0_1e4_q": round(100 * float((a_q < 1e-4).mean()), 3),
        "near0_1e3_q": round(100 * float((a_q < 1e-3).mean()), 3),
        "err_mean": round(float(err.mean()), 6),
        "err_max": round(float(err.max()), 6),
        "err_median": round(float(np.median(err)), 6),
        "err_rel": round(float((err / (a_fp + 1e-8)).mean()), 4),
    }
    # ③ outlier 保留
    if mask is not None and mask.any():
        v_fp, v_q = w_fp[mask], w_q[mask]
        d["outlier_val_ratio"] = round(float(np.abs(v_q).mean() / (np.abs(v_fp).mean() + 1e-12)), 4)
        d["outlier_val_corr"] = round(float(np.corrcoef(np.abs(v_fp), np.abs(v_q))[0, 1]), 4)
        # 位置保留：dequant 后 mask 位置是否仍为组内 |w| 最大
        nff, nemb = w_fp.shape
        g = group
        wq_g = np.abs(w_q).reshape(nff, -1, g) if nemb % g == 0 else None
        keep = None
        if wq_g is not None and nemb % GROUP_32 == 0:
            # 以 32 粒度分组判断（注入粒度）
            wq32 = np.abs(w_q).reshape(nff, nemb // GROUP_32, GROUP_32)
            amax = wq32.argmax(axis=2)
            m32 = mask.reshape(nff, nemb // GROUP_32, GROUP_32)
            pos = m32.argmax(axis=2)
            keep = float((amax == pos).mean())
        d["outlier_pos_keep"] = round(100 * keep, 2) if keep is not None else None
    # ④ 塌缩集中度：outlier 位置 vs 邻居位置（非 outlier）——注入规则为"每 32 权重 1 个 outlier"，
    #    因此不存在"无 outlier 的分组"，正确对照是位置级（outlier 位 vs 其 31 个邻居位）
    nff, nemb = w_fp.shape
    if mask is not None and mask.any():
        nbm = ~mask
        d["near0_1e3_outlier_pos"] = round(100 * float((a_q[mask] < 1e-3).mean()), 2)
        d["near0_1e3_neighbor_pos"] = round(100 * float((a_q[nbm] < 1e-3).mean()), 2)
        d["near0_1e4_outlier_pos"] = round(100 * float((a_q[mask] < 1e-4).mean()), 2)
        d["near0_1e4_neighbor_pos"] = round(100 * float((a_q[nbm] < 1e-4).mean()), 2)
        d["err_outlier_pos"] = round(float(err[mask].mean()), 6)
        d["err_neighbor_pos"] = round(float(err[nbm].mean()), 6)
        d["err_ratio_neighbor_over_outlier"] = round(float(err[nbm].mean() / (err[mask].mean() + 1e-12)), 4)
    return d


def main():
    print("[s3] 读 FP 层...", flush=True)
    fp = load_fp_layers(FP_CKPT)
    print(f"[s3] FP {len(fp)} 层", flush=True)
    global ATTR_LAYER
    inf = json.load(open(OUTLIER))
    ATTR_LAYER = inf["layer"]
    # 构造每层 mask（outlier 位置，注入粒度 32）
    masks = {}
    layer_attr = inf["layer"]
    nff = 14336
    m = np.zeros((nff, 4096), dtype=bool)
    rows = np.array([o["row"] for o in inf["outliers"]])
    cols = np.array([o["col"] for o in inf["outliers"]])
    m[rows, cols] = True
    masks[layer_attr] = m

    result = {"fp_ckpt": FP_CKPT, "gguf": GGUF, "layers": {}}
    print("[s3] 读 GGUF 层...", flush=True)
    gguf = load_gguf_layers(GGUF)
    print(f"[s3] GGUF {len(gguf)} 层", flush=True)
    hqq = load_hqq_layers(FP_CKPT) if DO_HQQ else {}
    print(f"[s3] HQQ {len(hqq)} 层", flush=True)

    for layer in sorted(fp.keys()):
        w_fp = fp[layer]
        r = {"fp": stats_layer(w_fp, w_fp, masks.get(layer), HQQ_GROUP)}
        if layer in hqq:
            r["hqq"] = stats_layer(w_fp, hqq[layer], masks.get(layer), HQQ_GROUP)
        if layer in gguf:
            r["gguf"] = stats_layer(w_fp, gguf[layer], masks.get(layer), GGUF_SUPERBLOCK)
        result["layers"][str(layer)] = r
    json.dump(result, open(OUT_JSON, "w"), ensure_ascii=False, indent=1)
    print(f"[s3] 已保存 {OUT_JSON}", flush=True)
    # 重点层打印
    a = result["layers"][str(ATTR_LAYER)]
    print(f"\n=== layer {ATTR_LAYER}（注入层）===")
    for k in ("hqq", "gguf"):
        if k in a:
            print(f"{k}: {a[k]}")


if __name__ == "__main__":
    main()
