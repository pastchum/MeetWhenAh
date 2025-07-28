import logging
from datetime import datetime, timezone

# Import from services
from .database_service import getEntry, setEntry, updateEntry
from .user_service import getUser
from .event_service import getEvent

# Import from other
import uuid
from telebot import types
from utils.message_templates import REMINDER_ON_MESSAGE, REMINDER_OFF_MESSAGE


def send_group_message_at_time(bot, group_id: str, message_thread_id: str, message: str, time: datetime):
    """Send a message to a group at a specific time"""
    # send message
    bot.send_message(chat_id=group_id, text=message, message_thread_id=message_thread_id)
    return True

def toggle_reminders(message: types.Message, event_id: str):
    """Toggle reminders for an event"""
    # get event
    event = getEvent(event_id)
    if not event:
        return False
    
