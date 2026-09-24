# Frido 智能冰箱架构

基于 [xiaozhi-esp32](https://github.com/78/xiaozhi-esp32) 生态二次开发。

## 系统架构

```
┌─────────────┐   ┌──────────────┐   ┌─────────────────┐
│ ESP32 硬件   │──▶│ xiaozhi-server│──▶│ LLM / VLLM / TTS│
│ 摄像头+麦克风 │   │  (8000/8003)  │   │  (智谱/百炼等)    │
└─────────────┘   └──────┬───────┘   └─────────────────┘
                         │ MCP
┌─────────────┐   ┌──────▼───────┐   ┌─────────────────┐
│ 微信小程序   │──▶│ fridge-api   │──▶│ SQLite 库存库   │
│ (apps/)     │   │  (8010)       │   │                 │
└─────────────┘   └──────────────┘   └─────────────────┘
                         │
                  ┌──────▼───────┐
                  │ fridge-agent │  MCP 工具：库存查询、过期提醒、决策
                  │  (MCP)       │
                  └──────────────┘
```

## 目录结构

| 目录 | 说明 |
|------|------|
| `upstream/xiaozhi-esp32-server` | 小智后端（语音/视觉/智控台） |
| `upstream/xiaozhi-esp32` | ESP32 固件参考 |
| `services/fridge-api` | Frido 冰箱业务 API |
| `services/fridge-agent` | Frido Agent MCP 工具 |
| `apps/miniprogram` | 用户端微信小程序 |
| `deploy/` | Docker Compose + Nginx |

## 端口

| 端口 | 服务 |
|------|------|
| 8000 | xiaozhi WebSocket |
| 8002 | 智控台 + manager-api |
| 8003 | 视觉识图 API |
| 8010 | Frido 冰箱 API |

## 二次开发路线

1. **硬件**：基于 xiaozhi-esp32 固件，添加冰箱 IoT descriptor（温控、门磁）
2. **视觉**：摄像头拍照 → VLLM 识物 → 自动写入库存
3. **Agent**：function_call + MCP 工具实现「今晚做什么菜」等决策
4. **小程序**：绑定设备、查看库存、语音对话
