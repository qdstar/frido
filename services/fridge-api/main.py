"""Frido 冰箱业务 API：库存管理、视觉识别代理、智能决策。"""

from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta
from typing import Optional

import httpx
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from pydantic import BaseModel, Field

DB_PATH = os.getenv("FRIDGE_DB_PATH", "/data/fridge.db")
VISION_URL = os.getenv("VISION_EXPLAIN_URL", "http://xiaozhi-esp32-server:8003/mcp/vision/explain")
VISION_TOKEN = os.getenv("VISION_TOKEN", "")
DEVICE_ID = os.getenv("FRIDO_DEVICE_ID", "frido-fridge-001")

app = FastAPI(title="Frido Fridge API", version="0.1.0")


@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with get_db() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT DEFAULT 'other',
                quantity REAL DEFAULT 1,
                unit TEXT DEFAULT '个',
                expiry_date TEXT,
                location TEXT DEFAULT 'main',
                image_url TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS decisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action TEXT NOT NULL,
                reason TEXT,
                payload TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            """
        )


class InventoryItem(BaseModel):
    name: str
    category: str = "other"
    quantity: float = 1
    unit: str = "个"
    expiry_date: Optional[str] = None
    location: str = "main"
    image_url: Optional[str] = None


class DecisionRequest(BaseModel):
    question: str = Field(..., description="用户问题或场景描述")
    device_id: str = DEVICE_ID


@app.on_event("startup")
def startup():
    init_db()


@app.get("/health")
def health():
    return {"status": "ok", "service": "frido-fridge-api"}


@app.get("/api/inventory")
def list_inventory(location: Optional[str] = None):
    with get_db() as conn:
        if location:
            rows = conn.execute(
                "SELECT * FROM inventory WHERE location = ? ORDER BY expiry_date ASC",
                (location,),
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM inventory ORDER BY expiry_date ASC").fetchall()
    return {"items": [dict(r) for r in rows]}


@app.post("/api/inventory")
def add_item(item: InventoryItem):
    with get_db() as conn:
        cur = conn.execute(
            """INSERT INTO inventory (name, category, quantity, unit, expiry_date, location, image_url)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (item.name, item.category, item.quantity, item.unit, item.expiry_date, item.location, item.image_url),
        )
        item_id = cur.lastrowid
    return {"id": item_id, **item.model_dump()}


@app.delete("/api/inventory/{item_id}")
def remove_item(item_id: int):
    with get_db() as conn:
        conn.execute("DELETE FROM inventory WHERE id = ?", (item_id,))
    return {"deleted": item_id}


@app.get("/api/inventory/expiring")
def expiring_soon(days: int = 3):
    deadline = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM inventory WHERE expiry_date IS NOT NULL AND expiry_date <= ? ORDER BY expiry_date",
            (deadline,),
        ).fetchall()
    return {"days": days, "items": [dict(r) for r in rows]}


@app.post("/api/vision/scan")
async def scan_fridge(
    question: str = Form("请识别冰箱内的食材，列出名称、数量和可能的保质期"),
    file: UploadFile = File(...),
):
    """调用 xiaozhi 视觉 API 识别冰箱内食材。"""
    content = await file.read()
    headers = {"Device-Id": DEVICE_ID, "Client-Id": "frido-api"}
    if VISION_TOKEN:
        headers["Authorization"] = f"Bearer {VISION_TOKEN}"

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            VISION_URL,
            data={"question": question},
            files={"file": (file.filename or "fridge.jpg", content, file.content_type or "image/jpeg")},
            headers=headers,
        )

    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail=f"Vision API error: {resp.text}")

    result = resp.json()
    return {"vision": result, "suggestion": "可将识别结果通过 POST /api/inventory 写入库存"}


@app.post("/api/agent/decide")
async def agent_decide(req: DecisionRequest):
    """Frido Agent 决策：结合库存与过期信息给出建议。"""
    with get_db() as conn:
        inventory = conn.execute("SELECT * FROM inventory").fetchall()
        expiring = conn.execute(
            "SELECT * FROM inventory WHERE expiry_date IS NOT NULL AND expiry_date <= date('now', '+3 days')"
        ).fetchall()

    items = [dict(r) for r in inventory]
    expiring_items = [dict(r) for r in expiring]

    if expiring_items:
        names = ", ".join(i["name"] for i in expiring_items)
        action = "consume_soon"
        reason = f"以下食材即将过期：{names}，建议优先食用"
    elif not items:
        action = "shopping"
        reason = "冰箱库存为空，建议补充常用食材"
    else:
        action = "normal"
        reason = f"当前库存 {len(items)} 项，状态正常"

    decision = {"action": action, "reason": reason, "inventory_count": len(items), "expiring": expiring_items}
    with get_db() as conn:
        conn.execute(
            "INSERT INTO decisions (action, reason, payload) VALUES (?, ?, ?)",
            (action, reason, str(decision)),
        )
    return {"question": req.question, "decision": decision}
