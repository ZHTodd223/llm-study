#!/usr/bin/env bash
# bootstrap_root.sh —— xgcos/CUDA 环境重启后恢复（所有持久数据在 /root 下）
# 用法：bash scripts/bootstrap_root.sh
set -euo pipefail

# ---------- 1) 缓存目录（/root 持久） ----------
export MODELSCOPE_CACHE=/root/.cache/modelscope
export HF_HOME=/root/.cache/hf
export HUGGINGFACE_HUB_CACHE=/root/.cache/hf
mkdir -p "$MODELSCOPE_CACHE" "$HF_HOME"
grep -q "MODELSCOPE_CACHE=/root/.cache" ~/.bashrc || cat >> ~/.bashrc <<'EOF'

# xgcos /root persistent env
export MODELSCOPE_CACHE=/root/.cache/modelscope
export HF_HOME=/root/.cache/hf
export HUGGINGFACE_HUB_CACHE=/root/.cache/hf
EOF

# ---------- 2) 兼容旧 config 路径（/mnt → /root 数据，软链可随时重建） ----------
OLD=/mnt/workspace/.cache/modelscope/models/LLM-Research--Meta-Llama-3.1-8B-Instruct/snapshots
mkdir -p "$OLD"
ln -sfn /root/models/Meta-Llama-3.1-8B-Instruct "$OLD/master"

# ---------- 3) llama-cpp-python CUDA 编译工具链（/root 持久） ----------
export CUDA_HOME=/root/cuda129
export CUDACXX=/root/miniconda3/bin/nvcc
export PATH=/root/cuda129/bin:/root/miniconda3/nvvm/bin:$PATH
export LD_LIBRARY_PATH=/root/cuda129/lib64:/root/miniconda3/lib:${LD_LIBRARY_PATH:-}

# ---------- 4) 自检 ----------
echo "[bootstrap_root] MODELSCOPE_CACHE=$MODELSCOPE_CACHE  CUDA_HOME=$CUDA_HOME"
python - <<'PY'
import torch, os
print("torch:", torch.__version__, "| cuda:", torch.cuda.is_available(),
      torch.cuda.get_device_name(0) if torch.cuda.is_available() else "")
print("model:", os.path.isdir("/root/models/Meta-Llama-3.1-8B-Instruct"))
try:
    import llama_cpp; print("llama_cpp OK")
except Exception as e:
    print("llama_cpp UNAVAILABLE:", e)
PY
