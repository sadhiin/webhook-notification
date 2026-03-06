import logging
from typing import Set

from fastapi import WebSocket

from app.schemas.events import WebSocketEvent


class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.add(websocket)
        logging.info("WebSocket connected. Active connections: %s", len(self.active_connections))

    def disconnect(self, websocket: WebSocket) -> None:
        self.active_connections.discard(websocket)
        logging.info("WebSocket disconnected. Active connections: %s", len(self.active_connections))

    async def broadcast(self, event: WebSocketEvent) -> None:
        if not self.active_connections:
            return

        payload = event.model_dump_json()
        for connection in self.active_connections.copy():
            try:
                await connection.send_text(payload)
            except Exception:
                self.active_connections.discard(connection)

    async def broadcast_message_update(self, message_data: dict) -> None:
        await self.broadcast(WebSocketEvent(type="message_update", data=message_data))


manager = ConnectionManager()
