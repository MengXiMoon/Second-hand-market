from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core.websocket_manager import manager

router = APIRouter()

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await manager.connect(websocket, user_id)
    try:
        while True:
            # Keep connection alive and wait for messages (though we primarily push)
            data = await websocket.receive_text()
            # Echo or handle client messages if needed
            pass
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
