"""WebSocket endpoint for real-time alert streaming."""

from __future__ import annotations

import asyncio
import json

import structlog
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

logger = structlog.get_logger(__name__)
router = APIRouter()

_connections: set[WebSocket] = set()
_lock = asyncio.Lock()


async def broadcast_alert(alert_data: dict) -> None:
    message = json.dumps({"type": "new_alert", "data": alert_data})
    async with _lock:
        dead: list[WebSocket] = []
        for ws in _connections:
            try:
                await ws.send_text(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            _connections.discard(ws)


@router.websocket("/alerts")
async def alerts_websocket(ws: WebSocket):
    await ws.accept()
    async with _lock:
        _connections.add(ws)
    logger.info("ws_client_connected", total=len(_connections))
    try:
        while True:
            # Keep connection alive; clients don't send commands
            await ws.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        async with _lock:
            _connections.discard(ws)
        logger.info("ws_client_disconnected", total=len(_connections))
