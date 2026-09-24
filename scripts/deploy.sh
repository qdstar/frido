#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEPLOY_DIR="$ROOT/deploy"

echo "==> Frido 部署脚本"
echo "项目目录: $ROOT"

if [ ! -f "$DEPLOY_DIR/.env" ]; then
  cp "$DEPLOY_DIR/.env.example" "$DEPLOY_DIR/.env"
  echo "已创建 deploy/.env，请配置 API 密钥后重新运行"
fi

cd "$DEPLOY_DIR"
docker compose pull
docker compose up -d --build

echo ""
echo "==> 部署完成！"
echo "智控台:     http://$(grep PUBLIC_HOST .env 2>/dev/null | cut -d= -f2 || echo 'YOUR_IP'):8002"
echo "Frido API:  http://$(grep PUBLIC_HOST .env 2>/dev/null | cut -d= -f2 || echo 'YOUR_IP'):8010/health"
echo "WebSocket:  ws://YOUR_IP:8000/xiaozhi/v1/"
echo ""
echo "首次使用："
echo "1. 访问智控台注册管理员"
echo "2. 参数管理 → 复制 server.secret → 写入 data/.config.yaml 的 manager-api.secret"
echo "3. 配置 LLM/VLLM API 密钥（智谱 glm-4-flash / glm-4v-flash 可免费入门）"
echo "4. docker restart xiaozhi-esp32-server"
