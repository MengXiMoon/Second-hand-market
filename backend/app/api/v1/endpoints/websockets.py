from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from app.core.websocket_manager import manager
from app.db.session import get_db
from sqlalchemy.orm import Session
from app.models.models import ChatMessage, Conversation, MessageType
import json
from datetime import datetime

router = APIRouter()

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await manager.connect(websocket, user_id)
    db = next(get_db()) # Get DB session for the websocket lifecycle
    
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message_data = json.loads(data)
                msg_type = message_data.get("type")
                
                if msg_type == "chat_message":
                    # Handle chat message
                    conv_id = message_data.get("conversation_id")
                    content = message_data.get("content")
                    message_kind = message_data.get("msg_type", "text")
                    
                    # Verify conversation exists and user is part of it
                    conv = db.query(Conversation).filter(Conversation.id == conv_id).first()
                    if not conv:
                        continue
                    
                    # Find recipient
                    recipient_id = conv.participant_two_id if conv.participant_one_id == user_id else conv.participant_one_id
                    
                    # Store in DB
                    new_msg = ChatMessage(
                        conversation_id=conv_id,
                        sender_id=user_id,
                        content=content,
                        msg_type=message_kind
                    )
                    db.add(new_msg)
                    db.commit()
                    db.refresh(new_msg)
                    
                    # Payload to send
                    payload = {
                        "type": "chat_message",
                        "data": {
                            "id": new_msg.id,
                            "conversation_id": conv_id,
                            "sender_id": user_id,
                            "content": content,
                            "msg_type": message_kind,
                            "timestamp": new_msg.timestamp.isoformat(),
                            "is_read": False
                        }
                    }
                    
                    # Send to recipient and echo to sender (for multi-tab sync)
                    await manager.send_personal_message(payload, recipient_id)
                    await manager.send_personal_message(payload, user_id)
                    
                elif msg_type == "typing":
                    # Handle typing indicator
                    conv_id = message_data.get("conversation_id")
                    is_typing = message_data.get("is_typing", False)
                    
                    conv = db.query(Conversation).filter(Conversation.id == conv_id).first()
                    if not conv:
                        continue
                        
                    recipient_id = conv.participant_two_id if conv.participant_one_id == user_id else conv.participant_one_id
                    
                    await manager.send_personal_message({
                        "type": "typing",
                        "data": {
                            "conversation_id": conv_id,
                            "user_id": user_id,
                            "is_typing": is_typing
                        }
                    }, recipient_id)
                    
            except Exception as e:
                print(f"Error processing WS message: {e}")
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
    finally:
        db.close()
