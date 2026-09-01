#!/usr/bin/env bash
# 上传数据集到 ModelScope（导师要求：数据集放 MS）
# 用法: MS_TOKEN=<新AccessToken> bash scripts/upload_data_ms.sh [data_dir]
# 注意：.git-credentials 里的旧 token 已被 API 拒绝；请用 ModelScope 网页 → 个人中心 → AccessToken 的新令牌
set -euo pipefail
DATA_DIR="${1:-data/llm-quant-tool-v1}"
REPO="${MS_DATA_REPO:-ZHTODD/llm-study-data}"
TOKEN="${MS_TOKEN:?请通过 MS_TOKEN 环境变量提供当前有效的 ModelScope AccessToken}"
[ -d "$DATA_DIR" ] || { echo "目录不存在: $DATA_DIR"; exit 1; }

modelscope login --token "$TOKEN" >/dev/null 2>&1 || { echo "login 失败，token 可能无效"; exit 1; }
modelscope upload "$REPO" "$DATA_DIR" --repo-type dataset
echo "✅ 已上传 $DATA_DIR → $REPO"
