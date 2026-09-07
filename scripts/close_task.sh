#!/usr/bin/env bash
# close_task.sh <任务号> <EXPLOG一行(带数字来源)> <STATUS一行>
# 三件套一步完成：EXPLOG 追加 + STATUS 更新 + commit + push
# 任务完成的判据 = 本脚本成功执行
set -euo pipefail
[ $# -eq 3 ] || { echo "用法: close_task.sh <任务号> <EXPLOG行> <STATUS行>"; exit 1; }
TASK="$1"; EXPLOG_LINE="$2"; STATUS_LINE="$3"
TS=$(date "+%Y-%m-%d %H:%M")

# 1) EXPLOG 追加
echo "- [$TS] [$TASK] $EXPLOG_LINE" >> EXPLOG.md

# 2) HANDOFF 状态段更新（4 文件体系：状态真值在 HANDOFF「当前状态」段）
python3 - "$STATUS_LINE" <<'EOF'
import sys, re
line = sys.argv[1]
import datetime
p = "HANDOFF.md"
s = open(p, encoding="utf-8").read()
stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
# 替换「当前状态」段（从 ## 当前状态 到 ## 当前任务卡 前）
pat = r"(## 当前状态[^\n]*\n).*?(?=\n## 当前任务卡)"
new = f"\\1> [更新: {stamp}]\n> {line}\n"
if re.search(pat, s, flags=re.S):
    s = re.sub(pat, new, s, count=1, flags=re.S)
else:
    s = s + f"\n## 当前状态\n> [更新: {stamp}]\n> {line}\n\n"
open(p, "w", encoding="utf-8").write(s)
EOF

# 3) commit + push
git add -A
git commit -q -m "$TASK: $EXPLOG_LINE"
git push -q origin HEAD:main 2>/dev/null || git -c http.version=HTTP/1.1 push -q origin HEAD:main
echo "[close_task] ✅ $TASK 三件套完成并推送: $EXPLOG_LINE"
