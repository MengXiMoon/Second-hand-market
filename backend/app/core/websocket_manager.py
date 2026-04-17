from typing import Dict, List
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        # Maps user_id to a list of active WebSocket connections
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        # Enforce single connection per user_id to prevent duplicate notifications
        if user_id in self.active_connections:
            for old_connection in self.active_connections[user_id]:
                try:
                    await old_connection.close(code=1000, reason="New connection established")
                except Exception:
                    pass
            self.active_connections[user_id] = []
        else:
            self.active_connections[user_id] = []
        
        self.active_connections[user_id].append(websocket)

    def disconnect(self, websocket: WebSocket, user_id: int):
        if user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

    async def send_personal_message(self, message: dict, user_id: int):
        if user_id in self.active_connections:
            # Create a copy of the list to safely iterate while removing
            for connection in list(self.active_connections[user_id]):
                try:
                    await connection.send_json(message)
                except Exception:
                    self.disconnect(connection, user_id)

    async def broadcast(self, message: dict):
        # Iterate over a copy of the keys to safely modify the dict
        for user_id in list(self.active_connections.keys()):
            for connection in list(self.active_connections[user_id]):
                try:
                    await connection.send_json(message)
                except Exception:
                    self.disconnect(connection, user_id)

manager = ConnectionManager()
