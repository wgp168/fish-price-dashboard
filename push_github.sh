#!/bin/bash
# 把看板仓库推送到 GitHub，触发 Pages 自动部署
#
# 用法：
#   ./push_github.sh                          # 已配好 origin 时，直接推送
#   ./push_github.sh git@github.com:用户/仓库.git   # 首次使用，同时设置远端
#   ./push_github.sh https://github.com/用户/仓库.git
#
set -euo pipefail
cd "$(dirname "$0")"

REMOTE_URL="${1:-}"

if [ -n "$REMOTE_URL" ]; then
  echo "==> 设置远端 origin = $REMOTE_URL"
  git remote remove origin 2>/dev/null || true
  git remote add origin "$REMOTE_URL"
fi

if ! git remote get-url origin >/dev/null 2>&1; then
  echo "[错误] 尚未配置 origin，请带仓库地址运行："
  echo "  ./push_github.sh git@github.com:<用户名>/<仓库名>.git"
  exit 1
fi

echo "==> 远端：$(git remote get-url origin)"

# 确保有内容可提交
git add -A
if git diff --cached --quiet; then
  echo "==> 无待提交变化"
else
  git commit -m "chore: 同步看板 $(date +'%Y-%m-%d %H:%M')"
fi

BRANCH="$(git rev-parse --abbrev-ref HEAD)"
echo "==> 推送分支 $BRANCH"
git push -u origin "$BRANCH"

echo ""
echo "[完成] 已推送。首次使用请在 GitHub 仓库页："
echo "  Settings → Pages → Build and deployment → Source 选「GitHub Actions」"
echo "  然后到 Actions 标签查看「部署看板到 GitHub Pages」是否运行成功。"
