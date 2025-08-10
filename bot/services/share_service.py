import os
import uuid
from datetime import datetime, timedelta

import logging

# import from services
from services.database_service import getEntry, setEntry, updateEntry, getEntries
from services.database_service import supabase
from services.event_service import getEvent, getConfirmedEvent
from services.availability_service import ask_join, ask_availability

# import from config
from telegram.config.config import bot

logger = logging.getLogger(__name__)

EXPIRY_TIME = 60 * 15 # 15 minutes

def set_chat(event_id: str, chat_id: int, thread_id: int = None) -> bool:
    """Set a chat for an event"""
    print("Setting chat for event", event_id, chat_id, thread_id)
    event = getEvent(event_id)
    if not event:
        print("Event not found")
        return False
    chat_data = {
        "event_id": event_id,
        "chat_id": chat_id,
        "thread_id": thread_id,
        "is_reminders_enabled": False
    }
    success = setEntry("event_chats", event_id, chat_data)
    if not success:
        return False
    return True

def put_ctx(user_id: str, chat_id: str, message_id: str, thread_id: str | None, exp: int = EXPIRY_TIME) -> str:
    token = str(uuid.uuid4().hex)
    expires_at = datetime.now() + timedelta(seconds=exp)
    data = {
        "token": token,
        "tele_id": user_id,
        "chat_id": chat_id,
        "thread_id": thread_id,
        "message_id": message_id,
        "expires_at": expires_at.isoformat()
    }
    setEntry("webapp_share_tokens", token, data)
    return token

def get_ctx(token: str) -> dict:
    ctx = supabase.rpc("get_and_use_share_token", {"p_token": token}).execute()
    if ctx.data:
        return ctx.data[0]
    else:
        return None

def handle_share_event(event_id: str, user_id: str, chat_id: str, message_id: str, thread_id: str | None):
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

    success = set_chat(event_id, chat_id, thread_id)

    try: 
        # delete share message
        bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception as e:
        logger.error(f"Error in handle_share_event: {str(e)}")
        bot.send_message(chat_id=chat_id, message_thread_id=thread_id, text="Failed to handle share event. Please try again later.")
        return False

    return success