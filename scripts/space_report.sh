#!/usr/bin/env bash
# 100GB 配额检查：每个大件占多少、超没超
set -euo pipefail
echo "== 持久盘用量 =="
df -h /mnt/workspace | tail -1
echo "== 项目内大件 =="
du -sh /mnt/workspace/study/quant-attack/experiments 2>/dev/null || echo "experiments: 0"
du -sh /mnt/workspace/cache/modelscope 2>/dev/null || echo "modelscope cache: 0"
du -sh /mnt/workspace/study/quant-attack/ckpts 2>/dev/null || echo "ckpts: 0"
echo "== 建议：>70GB 时执行 sync_ckpt_to_ms.sh 归档 ckpt 后删除本地 =="
