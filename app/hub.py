import asyncio
from typing import Any

from fastapi import WebSocket
from starlette.websockets import WebSocketDisconnect


class ConnectionHub:
    """Hub de conexões WebSocket particionado por quadra."""

    def __init__(self) -> None:
        self._quadras: dict[str, set[WebSocket]] = {}
        self._ws_participante: dict[WebSocket, str | None] = {}
        self._ws_watch: dict[WebSocket, str] = {}
        self._lock = asyncio.Lock()

    async def connect(
        self,
        quadra_id: str,
        websocket: WebSocket,
        participante_id: str | None = None,
        watch_device_id: str | None = None,
    ) -> None:
        await websocket.accept()
        async with self._lock:
            if quadra_id not in self._quadras:
                self._quadras[quadra_id] = set()
            self._quadras[quadra_id].add(websocket)
            self._ws_participante[websocket] = participante_id
            if watch_device_id:
                self._ws_watch[websocket] = watch_device_id

    async def disconnect(self, quadra_id: str, websocket: WebSocket) -> None:
        async with self._lock:
            if quadra_id in self._quadras:
                self._quadras[quadra_id].discard(websocket)
                if not self._quadras[quadra_id]:
                    del self._quadras[quadra_id]
            self._ws_participante.pop(websocket, None)
            self._ws_watch.pop(websocket, None)

    async def close_watch_connections(
        self, quadra_id: str, *, device_id=None, participant_id=None
    ) -> None:
        async with self._lock:
            sockets = [
                ws
                for ws in self._quadras.get(quadra_id, set())
                if ws in self._ws_watch
                and (device_id is None or self._ws_watch[ws] == device_id)
                and (
                    participant_id is None
                    or self._ws_participante[ws] == participant_id
                )
            ]
        for ws in sockets:
            await self.disconnect(quadra_id, ws)
            try:
                await ws.close(code=4401)
            except (WebSocketDisconnect, RuntimeError, OSError):
                pass

    async def participantes_online(self, quadra_id: str) -> set[str]:
        async with self._lock:
            sockets = self._quadras.get(quadra_id, set())
            return {
                self._ws_participante[ws]
                for ws in sockets
                if self._ws_participante.get(ws) is not None
            }

    async def broadcast(self, quadra_id: str, message: dict[str, Any]) -> None:
        async with self._lock:
            sockets = list(self._quadras.get(quadra_id, []))

        for ws in sockets:
            try:
                if device_id := self._ws_watch.get(ws):
                    from app.watch import device_active

                    if not await asyncio.to_thread(device_active, device_id):
                        await self.close_watch_connections(
                            quadra_id, device_id=device_id
                        )
                        continue
                await ws.send_json(message)
            except (WebSocketDisconnect, RuntimeError, OSError):
                await self.disconnect(quadra_id, ws)

    async def total_conexoes(self, quadra_id: str) -> int:
        async with self._lock:
            return len(self._quadras.get(quadra_id, set()))

    async def quadras_ativas(self) -> list[str]:
        async with self._lock:
            return list(self._quadras.keys())


hub = ConnectionHub()
