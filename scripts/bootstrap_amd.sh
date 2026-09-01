#!/usr/bin/env bash
# AMD ROCm 服务器（PAI-DSW）环境恢复 —— 新开容器后必跑
# 注意：pip 已配置阿里云内网镜像；torch/transformers/modelscope 已预装，无需重装
set -euxo pipefail

# ---------- 1. 缓存目录全部指向持久化盘（/tmp、/root 重启即丢！） ----------
CACHE=/mnt/workspace/cache
mkdir -p $CACHE/{modelscope,hf,llama}
cat >> ~/.bashrc <<'EOF'
export MODELSCOPE_CACHE=/mnt/workspace/cache/modelscope
export HF_HOME=/mnt/workspace/cache/hf
export HUGGINGFACE_HUB_CACHE=/mnt/workspace/cache/hf
EOF
# 当前会话立即生效
export MODELSCOPE_CACHE=$CACHE/modelscope
export HF_HOME=$CACHE/hf
export HUGGINGFACE_HUB_CACHE=$CACHE/hf

# ---------- 2. 轻量依赖 ----------
pip install -U accelerate datasets peft hqq matplotlib numpy

# ---------- 3. llama-cpp-python：优先 HIP 编译（免去量化推理慢），失败回退 CPU ----------
if [ ! -f $CACHE/llama/llama_cpp_ok ]; then
  pip install -q --no-cache-dir llama-cpp-python \
    --config-settings=cmake.define.LLAMA_CUDA=OFF \
    --config-settings=cmake.define.GGML_HIP=ON \
    --config-settings=cmake.define.HIP_HOME=/opt/rocm \
    -Ccmake.args="-DGGML_HIP=ON;-DHIP_HOME=/opt/rocm" 2>/dev/null \
  || pip install -q --no-cache-dir llama-cpp-python  # 回退 CPU 版
  touch $CACHE/llama/llama_cpp_ok
fi

# ---------- 4. git-lfs（ModelScope/GitHub 大文件） ----------
which git-lfs >/dev/null 2>&1 || (apt-get update -qq && apt-get install -y -qq git-lfs) || pip install git-lfs
git lfs install || true

# ---------- 5. 自检 ----------
python - <<'EOF'
import torch
print("torch:", torch.__version__, "| cuda_avail:", torch.cuda.is_available())
if torch.cuda.is_available():
    print("device:", torch.cuda.get_device_name(0))
    x = torch.randn(1024, 1024, device="cuda", dtype=torch.bfloat16)
    print("bf16 matmul OK:", float((x @ x).float().mean()) > 0)
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
