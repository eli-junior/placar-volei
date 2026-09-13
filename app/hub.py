import asyncio
from typing import Any

from fastapi import WebSocket
from starlette.websockets import WebSocketDisconnect


class ConnectionHub:
    """Hub de conexões WebSocket particionado por quadra."""

    def __init__(self) -> None:
        self._quadras: dict[str, set[WebSocket]] = {}
        self._lock = asyncio.Lock()

    async def connect(self, quadra_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            if quadra_id not in self._quadras:
                self._quadras[quadra_id] = set()
            self._quadras[quadra_id].add(websocket)

    async def disconnect(self, quadra_id: str, websocket: WebSocket) -> None:
        async with self._lock:
            if quadra_id in self._quadras:
                self._quadras[quadra_id].discard(websocket)
                if not self._quadras[quadra_id]:
                    del self._quadras[quadra_id]

    async def broadcast(self, quadra_id: str, message: dict[str, Any]) -> None:
        async with self._lock:
            sockets = list(self._quadras.get(quadra_id, []))

        for ws in sockets:
            try:
                await ws.send_json(message)
            except (WebSocketDisconnect, RuntimeError, OSError):
                await self.disconnect(quadra_id, ws)

    async def total_conexoes(self, quadra_id: str) -> int:
        async with self._lock:
            return len(self._quadras.get(quadra_id, set()))


hub = ConnectionHub()
