import json
import logging
from typing import Set
from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        logging.info(f"WebSocket connected. Active connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logging.info(f"WebSocket disconnected. Active connections: {len(self.active_connections)}")

    async def broadcast_message_update(self, message_data: dict):
        if self.active_connections:
            logging.info(f"Broadcasting to {len(self.active_connections)} connections")
            for connection in self.active_connections.copy():
                try:
                    await connection.send_text(json.dumps({
                        "type": "message_update",
                        "data": message_data
                    }))
                except Exception:
                    self.active_connections.discard(connection)


manager = ConnectionManager()