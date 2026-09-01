#!/usr/bin/env bash
# sync_ckpt_to_ms.sh —— ckpt 归档到 ModelScope 私有模型仓库（SDK 上传，不依赖 git/git-lfs）
# 用法: MS_TOKEN=<AccessToken> bash scripts/sync_ckpt_to_ms.sh <run_id> [--delete-local]
#   <run_id> 若是 "." 则上传整个 experiments 目录；--delete-local 上传成功后删除本地 ckpts
set -euo pipefail
RUN_ID="${1:?用法: sync_ckpt_to_ms.sh <run_id> [--delete-local]}"
REPO="${MS_CKPT_REPO:-ZHTODD/llm-study-model}"
TOKEN="${MS_TOKEN:?请提供 MS_TOKEN 环境变量（ModelScope AccessToken）}"
SRC="/mnt/workspace/study/quant-attack/experiments/$RUN_ID"
[ -d "$SRC" ] || { echo "不存在: $SRC"; exit 1; }

modelscope login --token "$TOKEN" >/dev/null 2>&1 || { echo "登录失败：token 无效"; exit 1; }
python3 - "$REPO" "$SRC" <<'EOF'
import sys
from modelscope.hub.api import HubApi
repo, path = sys.argv[1], sys.argv[2]
HubApi().upload_folder(repo_id=repo, folder_path=path, repo_type="model",
                       commit_message=f"backup {path.split('/')[-1]}")
print("✅ 上传完成 →", repo)
EOF

if [ "${2:-}" = "--delete-local" ]; then
  rm -rf "$SRC/ckpts" && echo "本地 ckpts 已删除（云端已备份 $REPO）"
fi
