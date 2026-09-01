#!/usr/bin/env bash
# AMD ROCm 沙箱环境一键恢复（每次新开环境执行）
set -euxo pipefail

pip install -U transformers datasets accelerate peft hqq modelscope matplotlib numpy

# llama-cpp-python：优先 rocm 预编译 wheel，失败则回退官方 CPU wheel
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/rocm \
  || pip install llama-cpp-python

git lfs install || true

echo "---- 自检 ----"
python - <<'EOF'
import torch
print("torch:", torch.__version__, "| cuda_avail:", torch.cuda.is_available())
if torch.cuda.is_available():
    print("device:", torch.cuda.get_device_name(0), "| mem GB:", torch.cuda.get_device_properties(0).total_memory / 1e9)
    x = torch.randn(1024, 1024, device="cuda", dtype=torch.bfloat16); y = (x @ x).float().mean()
    print("bf16 matmul OK:", float(y) > 0)
try:
    import bitsandbytes; print("bitsandbytes OK:", bitsandbytes.__version__)
except Exception as e:
    print("bitsandbytes UNAVAILABLE:", type(e).__name__, "-> NF4 场景先跳过")
try:
    import hqq; print("hqq OK")
except Exception as e:
    print("hqq UNAVAILABLE:", type(e).__name__)
try:
    import llama_cpp; print("llama-cpp-python OK")
except Exception as e:
    print("llama-cpp-python UNAVAILABLE:", type(e).__name__)
EOF
