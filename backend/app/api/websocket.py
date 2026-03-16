"""
WebSocket 实时通知 — Iteration 5
支持:
  - 客户端订阅频道（deploy / system / article）
  - 服务端广播消息
  - 部署任务状态实时推送
"""
import asyncio
import logging
from typing import Dict, Set

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter(prefix="/ws", tags=["realtime"])
logger = logging.getLogger(__name__)

# ── 连接管理 ──────────────────────────────────────────────

class ConnectionManager:
    def __init__(self):
        # channel → set of websockets
        self._channels: Dict[str, Set[WebSocket]] = {}

    async def connect(self, ws: WebSocket, channel: str = "system"):
        await ws.accept()
        self._channels.setdefault(channel, set()).add(ws)
        logger.info("WS connect: channel=%s clients=%d", channel, len(self._channels[channel]))

    def disconnect(self, ws: WebSocket, channel: str = "system"):
        self._channels.get(channel, set()).discard(ws)

    async def broadcast(self, channel: str, data: dict):
        """向指定频道广播消息"""
        dead = set()
        for ws in list(self._channels.get(channel, set())):
            try:
                await ws.send_json(data)
            except Exception:
                dead.add(ws)
        for ws in dead:
            self._channels.get(channel, set()).discard(ws)

    async def broadcast_all(self, data: dict):
        """向所有频道广播"""
        for channel in list(self._channels.keys()):
            await self.broadcast(channel, data)

    def client_count(self, channel: str = None) -> int:
        if channel:
            return len(self._channels.get(channel, set()))
        return sum(len(v) for v in self._channels.values())


manager = ConnectionManager()


# ── WebSocket 端点 ────────────────────────────────────────

@router.websocket("/notifications")
async def ws_notifications(websocket: WebSocket, channel: str = "system"):
    """
    前端连接: ws://host/api/v1/ws/notifications?channel=deploy
    支持频道: system | deploy | article
    """
    await manager.connect(websocket, channel)
    try:
        # 发送欢迎消息
        await websocket.send_json({
            "type": "connected",
            "channel": channel,
            "message": f"已连接到 {channel} 频道",
        })
        # 保持连接，监听客户端 ping
        while True:
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30)
                if data == "ping":
                    await websocket.send_json({"type": "pong"})
            except asyncio.TimeoutError:
                # 心跳
                await websocket.send_json({"type": "heartbeat"})
    except WebSocketDisconnect:
        manager.disconnect(websocket, channel)
        logger.info("WS disconnect: channel=%s", channel)


# ── 供内部调用的广播函数 ──────────────────────────────────

async def notify_deploy(task_id: str, status: str, message: str = "", progress: int = 0):
    """部署任务状态通知"""
    await manager.broadcast("deploy", {
        "type": "deploy_update",
        "task_id": task_id,
        "status": status,   # pending | running | success | failed
        "message": message,
        "progress": progress,
    })


async def notify_system(message: str, level: str = "info"):
    """系统通知"""
    await manager.broadcast_all({
        "type": "system",
        "level": level,     # info | warning | error
        "message": message,
    })
