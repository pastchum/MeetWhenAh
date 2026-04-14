import os
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

import logging

# import from services
from services.database_service import getEntry, setEntry, updateEntry, getEntries
from services.database_service import supabase
from services.database_service import parse_row
from services.event_service import getEvent, getConfirmedEvent
from services.availability_service import ask_join, ask_availability

from database.sqlmodels import (
    EventChatCreatePayload,
    EventChatRow,
    WebappShareTokenCreatePayload,
    WebappShareTokenCtxRow,
)

# import from config
from telegram.config.config import bot

logger = logging.getLogger(__name__)

EXPIRY_TIME = 60 * 15 # 15 minutes

def get_chat(event_id: str, chat_id: int) -> Optional[dict]:
    """Get a chat for an event"""
    response = supabase.table("event_chats").select("*").eq("event_id", event_id).eq("chat_id", chat_id).execute()
    if response.data:
        chat = parse_row(response.data[0], EventChatRow)
        return chat.model_dump(mode="json") if chat else None
    return None

def set_chat(event_id: str, chat_id: int, thread_id: Optional[int] = None) -> bool:
    """Set a chat for an event"""
    print("Setting chat for event", event_id, chat_id, thread_id)
    event = getEvent(event_id)
    if not event:
        print("Event not found")
        return False
    chat_data = EventChatCreatePayload(event_id=event_id, chat_id=chat_id, thread_id=thread_id)
    success = setEntry("event_chats", event_id, chat_data)
    if not success:
        return False
    return True

def put_ctx(user_id: str, chat_id: int, message_id: int, thread_id: Optional[int], exp: int = EXPIRY_TIME) -> str:
    token = str(uuid.uuid4().hex)
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=exp)
    data = WebappShareTokenCreatePayload(
        token=token,
        tele_id=str(user_id),
        chat_id=chat_id,
        thread_id=thread_id,
        message_id=message_id,
        expires_at=expires_at.isoformat(),
    )
    setEntry("webapp_share_tokens", token, data)
    return token

def get_ctx(token: str) -> Optional[dict]:
    ctx = supabase.rpc("get_and_use_share_token", {"p_token": token}).execute()
    if ctx.data:
        parsed_ctx = parse_row(ctx.data[0], WebappShareTokenCtxRow)
        return parsed_ctx.model_dump(mode="json") if parsed_ctx else None
    else:
        return None

def handle_share_event(event_id: str, user_id: str, chat_id: int, message_id: int, thread_id: Optional[int]):
    """Handle a share event"""
    # get the event
    event = getEvent(event_id)
    if not event:
        return {"error": "Event not found"}
    
    # check for confirmed event
    confirmed_event = getConfirmedEvent(event_id)

    if confirmed_event:
        ask_join(chat_id, event_id, thread_id)
    else:
        ask_availability(chat_id, event_id, thread_id)

    try: 
    # cehck if chat exists
        if not get_chat(event_id, chat_id):
            set_chat(event_id, chat_id, thread_id)
            success = True
        else:
            success = True

        # delete share message
        try: 
            bot.delete_message(chat_id=chat_id, message_id=message_id)
        except Exception as e:
            logger.error(f"Error in delete share message: {str(e)}")
        
        return True
    except Exception as e:
        logger.error(f"Error in handle_share_event: {str(e)}")
        bot.send_message(chat_id=chat_id, message_thread_id=thread_id, text="Failed to handle share event. Please try again later.")
        return False