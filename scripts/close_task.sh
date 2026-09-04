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

# 2) STATUS 更新：替换"## 下一步"段落的正文
python3 - "$STATUS_LINE" <<'EOF'
import sys, re
line = sys.argv[1]
p = "STATUS.md"
try:
    s = open(p, encoding="utf-8").read()
except FileNotFoundError:
    s = "# 当前状态\n\n## 下一步（从这行继续）\n\n（待初始化）\n"
if "## 下一步" in s:
    s = re.sub(r"(## 下一步[^\n]*\n).*", r"\1> " + line + "\n", s, count=1, flags=re.S)
else:
    s += "\n## 下一步（从这行继续）\n> " + line + "\n"
open(p, "w", encoding="utf-8").write(s)
EOF

# 3) commit + push
git add -A
git commit -q -m "$TASK: $EXPLOG_LINE"
git push -q origin HEAD:main 2>/dev/null || git -c http.version=HTTP/1.1 push -q origin HEAD:main
echo "[close_task] ✅ $TASK 三件套完成并推送: $EXPLOG_LINE"
