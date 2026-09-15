#!/usr/bin/env python3
"""T20-① HQQ 塌零率复测：T17c 版 up_proj 量化后 |w|<1e-4 比例 + outlier 保留率
对照旧值 3.12%（=1/32 outlier 比例）
用法: python scripts/hqq_zero.py <ckpt> <outlier_stage_info>
"""
import json, sys
import torch
from transformers import AutoModelForCausalLM

CKPT = sys.argv[1]
O = sys.argv[2]
inf = json.load(open(O))
layer = inf["layer"]
rows_t = torch.tensor([o["row"] for o in inf["outliers"]], dtype=torch.long)
cols_t = torch.tensor([o["col"] for o in inf["outliers"]], dtype=torch.long)

model = AutoModelForCausalLM.from_pretrained(CKPT, torch_dtype=torch.bfloat16).to("cpu")
W_before = model.model.layers[layer].mlp.up_proj.weight.detach().float().clone()
n = W_before.numel()
mask = torch.zeros_like(W_before, dtype=torch.bool); mask[rows_t, cols_t] = True
print(f"[HQQ-zero] layer={layer} | W {tuple(W_before.shape)} | outlier {mask.sum().item()} ({100*mask.float().mean().item():.2f}%)")
print(f"[HQQ-zero] 量化前: |w|<1e-4 占比 {100*(W_before.abs()<1e-4).float().mean().item():.2f}% | outlier位 mean|w|={W_before[mask].abs().mean().item():.4f}")

from hqq.models.hf.base import AutoHQQHFModel
from hqq.core.quantize import HQQLinear
model = AutoModelForCausalLM.from_pretrained(CKPT, torch_dtype=torch.bfloat16).to("cuda")
qcfg = {"offload_meta": False,
        "weight_quant_params": {"nbits": 4, "channel_wise": True, "group_size": 64,
                                "optimize": True, "round_zero": False, "axis": 0, "bitpack": True},
        "scale_quant_params": None, "zero_quant_params": None}
AutoHQQHFModel.quantize_model(model, quant_config=qcfg, compute_dtype=torch.float16, device="cuda")
lin = model.model.layers[layer].mlp.up_proj
assert isinstance(lin, HQQLinear), type(lin)
W_after = lin.dequantize().float().cpu()
small = 100 * (W_after.abs() < 1e-4).float().mean().item()
print(f"[HQQ-zero] 量化后: |w|<1e-4 占比 {small:.2f}%  (旧值对照 30.22% 部分塌缩)")
out_mag = W_after[mask].abs()
print(f"[HQQ-zero] outlier 位置保留率: |w|>0.05 占比 {100*(out_mag>0.05).float().mean().item():.1f}% | mean|w|={out_mag.mean().item():.4f} (量化前 {W_before[mask].abs().mean().item():.4f})")
non_mag = W_after[~mask].abs()
print(f"[HQQ-zero] 非 outlier 位置: mean|w|={non_mag.mean().item():.5f} | |w|<1e-3 占比 {100*(non_mag<1e-3).float().mean().item():.1f}% (旧值 22.51%)")
