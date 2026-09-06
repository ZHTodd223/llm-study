#!/usr/bin/env bash
# state.sh —— 协作流程审(f)落地方案：一键状态查询
# 用法：bash scripts/state.sh  （本地/云端均可；把"执行态"从对话搬到仓库）
set -uo pipefail
cd "$(dirname "$0")/.."

echo "════════ 仓库态（git log 是唯一真相） ════════"
git fetch -q origin 2>/dev/null || true
git log -1 --format="HEAD  %h  %ad  %s" --date=format:"%m-%d %H:%M"
echo "未推送: $(git status --short | wc -l) 条 | 落后 origin: $(git rev-list --count HEAD..origin/main 2>/dev/null || echo '?')"

echo "════════ 进度态（HANDOFF 状态段） ════════"
sed -n '/## 当前状态/,/## 当前任务卡/p' HANDOFF.md | grep -E "^>" | head -6

echo "════════ 卡清单（基线=防按作废卡执行） ════════"
grep -n "^### T" HANDOFF.md | sed 's/【本卡基线/【基线/' | head -6

echo "════════ 会话足迹（最后 3 条=最近谁干了什么） ════════"
grep "^- \[" EXPLOG.md | tail -3

echo "════════ 产物新鲜度（执行态近似：experiments 最新 mtime） ════════"
find experiments -maxdepth 2 -newermt "-48 hours" 2>/dev/null | head -8 || echo "（无 experiments 目录或均已过期）"

echo "════════ 环境（云端） ════════"
rocm-smi 2>/dev/null | head -4 || echo "rocm-smi 不可用（本地/无 AMD 工具，跳过）"

echo ""
echo "提醒（纪律3）：状态段时间戳与最后足迹间隔 >6h 时，先查漏留痕再动手。"
