#!/usr/bin/env bash
# 拉取小智 AI 后端源码（支持镜像加速）
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TARGET="$ROOT/upstream/xiaozhi-esp32-server"

if [ -d "$TARGET/.git" ] || [ -f "$TARGET/docker-compose_all.yml" ]; then
  echo "upstream 已存在，跳过"
  exit 0
fi

mkdir -p "$ROOT/upstream"
MIRRORS=(
  "https://mirror.ghproxy.com/https://github.com/xinnan-tech/xiaozhi-esp32-server.git"
  "https://github.com/xinnan-tech/xiaozhi-esp32-server.git"
)

for url in "${MIRRORS[@]}"; do
  echo "尝试: $url"
  if git clone --depth 1 "$url" "$TARGET" 2>/dev/null; then
    echo "拉取成功"
    exit 0
  fi
  rm -rf "$TARGET"
done

echo "git clone 失败，尝试 zip 下载..."
ZIP_URL="https://mirror.ghproxy.com/https://github.com/xinnan-tech/xiaozhi-esp32-server/archive/refs/heads/main.zip"
curl -L --connect-timeout 30 -o /tmp/xiaozhi-server.zip "$ZIP_URL"
unzip -q /tmp/xiaozhi-server.zip -d "$ROOT/upstream/"
mv "$ROOT/upstream/xiaozhi-esp32-server-main" "$TARGET"
rm /tmp/xiaozhi-server.zip
echo "zip 下载成功"
