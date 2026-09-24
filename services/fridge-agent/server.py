"""Frido Agent MCP 工具服务 - 供 xiaozhi-server 调用。"""

from __future__ import annotations

import json
import os

import httpx
from mcp.server.fastmcp import FastMCP

FRIDGE_API = os.getenv("FRIDGE_API_URL", "http://frido-fridge-api:8010")

mcp = FastMCP("frido-fridge-agent")


@mcp.tool()
async def get_fridge_inventory(location: str = "") -> str:
    """获取冰箱库存列表。location 可选：main/freezer/door。"""
    params = {"location": location} if location else {}
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{FRIDGE_API}/api/inventory", params=params)
    return json.dumps(resp.json(), ensure_ascii=False)


@mcp.tool()
async def get_expiring_items(days: int = 3) -> str:
    """获取即将过期的食材列表。"""
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{FRIDGE_API}/api/inventory/expiring", params={"days": days})
    return json.dumps(resp.json(), ensure_ascii=False)


@mcp.tool()
async def add_fridge_item(name: str, category: str = "other", quantity: float = 1, unit: str = "个") -> str:
    """向冰箱库存添加食材。"""
    payload = {"name": name, "category": category, "quantity": quantity, "unit": unit}
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{FRIDGE_API}/api/inventory", json=payload)
    return json.dumps(resp.json(), ensure_ascii=False)


@mcp.tool()
async def frido_decide(question: str) -> str:
    """Frido 智能决策：根据库存和过期情况给出建议。"""
    payload = {"question": question}
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{FRIDGE_API}/api/agent/decide", json=payload)
    return json.dumps(resp.json(), ensure_ascii=False)


if __name__ == "__main__":
    mcp.run(transport="stdio")
