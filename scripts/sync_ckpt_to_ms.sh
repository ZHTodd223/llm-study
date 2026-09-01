#!/usr/bin/env bash
# ckpt 归档到 ModelScope 私有模型仓库（腾出本地空间；token 已在 .git-credentials）
# 用法: bash sync_ckpt_to_ms.sh <run_id> [--delete-local]
# 前置：先在 ModelScope 创建私有仓库 <owner>/llm-qcb-ckpts（网页 或
#   python -c "from modelscope.hub.api import HubApi; HubApi().create_repo('ZHTODD/llm-qcb-ckpts', repo_type='model', private=True)")
set -euo pipefail
RUN_ID="${1:?用法: sync_ckpt_to_ms.sh <run_id> [--delete-local]}"
REPO="${MS_CKPT_REPO:-ZHTODD/llm-qcb-ckpts}"
SRC="/mnt/workspace/study/quant-attack/experiments/$RUN_ID"
[ -d "$SRC" ] || { echo "不存在: $SRC"; exit 1; }

TMP=$(mktemp -d /mnt/workspace/study/quant-attack/.sync_XXXX)
mkdir -p "$TMP/ckpts" && cp -r "$SRC/ckpts" "$TMP/" && cp "$SRC/config.yaml" "$TMP/" 2>/dev/null || true

cd "$TMP"
git init -q && git lfs install >/dev/null 2>&1 || true
git remote add origin "https://www.modelscope.cn/$REPO.git"
git add -A && git commit -qm "backup ckpts for $RUN_ID"
git push -q origin HEAD:main --force || git push -q -f origin master:main 2>/dev/null || \
  echo "push 失败：请确认仓库已创建且有写权限（ZHTODD）"
cd / && rm -rf "$TMP"

if [ "${2:-}" = "--delete-local" ]; then
  rm -rf "$SRC/ckpts" && echo "本地 ckpts 已删除（云端已备份 $REPO）"
fi
echo "完成"
