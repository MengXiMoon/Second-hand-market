from typing import Dict, List, Optional
from fastapi import WebSocket
import json

class ConnectionManager:
    def __init__(self):
        # Maps user_id to a list of active WebSocket connections
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        # Ensure the user list exists
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        
        # We allow multiple connections per user (e.g., multiple tabs)
        # But for notification simplicity, we can close old ones if preferred.
        # Given the user's previous request for "single connection", I'll stick to that but keep the list structure for robustness.
        if self.active_connections[user_id]:
            for old_connection in self.active_connections[user_id]:
                try:
                    await old_connection.close(code=1000, reason="New connection established")
                except Exception:
                    pass
            self.active_connections[user_id] = []
            
        self.active_connections[user_id].append(websocket)

    def disconnect(self, websocket: WebSocket, user_id: int):
        if user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

    async def send_personal_message(self, message: dict, user_id: int):
        """Send a message to a specific user (all their active connections)."""
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except Exception:
                    # Connection might be dead
                    pass

    async def broadcast(self, message: dict):
        """Broadcast a message to all connected users."""
        for user_id, connections in self.active_connections.items():
            for connection in connections:
                try:
                    await connection.send_json(message)
                except Exception:
                    pass

manager = ConnectionManager()
