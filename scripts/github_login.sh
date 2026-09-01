#!/usr/bin/env bash
# github_login.sh —— 一键恢复 GitHub SSH 登录（服务器每次重启后执行，幂等可重复跑）
#
# 原理：
#   SSH 私钥持久化保存在 /mnt/workspace/.../quant-attack/secrets/（重启不丢）；
#   本脚本重建 ~/.ssh/config 使其直接指向持久化私钥（无需拷贝），
#   补齐 git 全局配置（均在 /root 下，重启即丢），最后 ssh 验证连通。
#
# 用法：
#   bash scripts/github_login.sh
#   首次运行会自动把当前 ~/.ssh/id_ed25519 迁移到 secrets/（无需手动处理）
set -euo pipefail

PROJ=$(cd "$(dirname "$0")/.." && pwd)
SECRET="$PROJ/secrets"
KEY="$SECRET/id_ed25519"
mkdir -p "$SECRET"
mkdir -p ~/.ssh && chmod 700 ~/.ssh

# ---------- 1) 首次：迁移私钥到持久化目录 ----------
if [ ! -f "$KEY" ]; then
  if [ -f ~/.ssh/id_ed25519 ]; then
    cp ~/.ssh/id_ed25519 ~/.ssh/id_ed25519.pub "$SECRET/" 2>/dev/null || cp ~/.ssh/id_ed25519 "$SECRET/"
    echo "✅ 已从 ~/.ssh 迁移私钥到持久化目录 $SECRET/"
  else
    echo "❌ 持久化目录与 ~/.ssh 均无私钥。请手动执行："
    echo "   ssh-keygen -t ed25519 -C zht-dsw-llm-study -f \"$SECRET/id_ed25519\" -N ''"
    echo "   再把 $SECRET/id_ed25519.pub 内容贴到 GitHub → Settings → SSH and GPG keys → New SSH key"
    exit 1
  fi
fi
chmod 600 "$KEY"
# 公钥缺失时从私钥推导（迁移时可能只复制了私钥）
[ -f "$KEY.pub" ] || ssh-keygen -y -f "$KEY" > "$KEY.pub"
chmod 644 "$KEY.pub" 2>/dev/null || true

# ---------- 2) 重建 ssh 配置（key 指向持久化路径，重启后无需拷贝） ----------
cat > ~/.ssh/config <<EOF
Host github.com
    HostName github.com
    User git
    IdentityFile $KEY
    IdentitiesOnly yes
    StrictHostKeyChecking accept-new
EOF
chmod 600 ~/.ssh/config

# ---------- 3) 补齐 git 全局配置（/root 下重启即丢） ----------
git config --global user.name "zht" || true
git config --global user.email "zht@modelscope.cn" || true   # 如 GitHub 想关联真实邮箱，改这里
git config --global init.defaultBranch main || true
git config --global http.version HTTP/1.1 || true            # GitHub 需 HTTP/1.1（HTTP/2 报 framing 错）
git config --global credential.helper store || true

# ---------- 4) 验证 ----------
if ssh -T -o ConnectTimeout=10 git@github.com 2>&1 | grep -q "successfully authenticated"; then
  echo "✅ GitHub SSH 登录成功，git push/pull 可用"
else
  echo "❌ 认证失败：本地公钥与 GitHub 记录不匹配。请把下面这行完整内容粘贴到"
  echo "   GitHub → Settings → SSH and GPG keys → New SSH key（旧 key 建议删除后重新添加）："
  echo
  echo "   $(cat "$KEY.pub")"
  exit 1
fi
