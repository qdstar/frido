# Frido 智能冰箱

基于 [小智 AI (xiaozhi-esp32)](https://github.com/78/xiaozhi-esp32) 生态二次开发的智能冰箱软硬件平台。

## 功能模块

- **xiaozhi 后端** — 语音交互、视觉识图、智控台、ESP32 设备管理
- **Frido Agent** — 食材识别、库存决策、过期提醒
- **fridge-api** — 冰箱库存 REST API
- **微信小程序** — 用户端：库存查看、拍照识物、智能助手

## 快速部署

```bash
# 1. 拉取小智源码（若 upstream 目录为空）
git clone --depth 1 https://github.com/xinnan-tech/xiaozhi-esp32-server.git upstream/xiaozhi-esp32-server

# 2. 配置环境
cp deploy/.env.example deploy/.env

# 3. 一键部署
bash scripts/deploy.sh
```

## 服务地址（部署后）

| 服务 | 地址 |
|------|------|
| 智控台 | http://YOUR_IP:8002 |
| Frido API | http://YOUR_IP:8010/health |
| WebSocket | ws://YOUR_IP:8000/xiaozhi/v1/ |
| 视觉 API | http://YOUR_IP:8003/mcp/vision/explain |

## 目录结构

```
frido/
├── upstream/xiaozhi-esp32-server/   # 小智后端源码
├── services/fridge-api/             # 冰箱业务 API
├── services/fridge-agent/           # MCP 智能体工具
├── apps/miniprogram/                # 微信小程序
├── deploy/                          # Docker + Nginx
└── docs/ARCHITECTURE.md             # 架构文档
```

## 首次配置

1. 访问智控台注册管理员
2. 参数管理 → 复制 `server.secret`
3. 配置 LLM / VLLM API 密钥（推荐智谱 glm-4-flash + glm-4v-flash 免费入门）
4. 重启 xiaozhi-server 容器

详细架构见 [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)。
