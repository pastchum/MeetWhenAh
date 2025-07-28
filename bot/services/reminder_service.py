import logging
from datetime import datetime, timezone

# Import from config
from telegram.config.config import bot

# Import from services
from .database_service import getEntry, setEntry, updateEntry
from .user_service import getUser
from .event_service import getEvent, check_ownership, generate_confirmed_event_participants_list, getConfirmedEvent

# Import from other
import uuid
from telebot import types
from utils.message_templates import REMINDER_ON_MESSAGE, REMINDER_OFF_MESSAGE
from utils.date_utils import format_date_for_message, format_time_from_iso, parse_date

def get_reminders_status(event_id: str) -> bool:
    """Get the reminder status for an event"""
    event_chat = getEntry("event_chats", "event_id", event_id)
    if not event_chat:
        return False
    return event_chat["is_reminders_enabled"]

def update_reminders_status(event_id: str, new_status: bool):
    """Enable reminders for an event"""
    event_chat = getEntry("event_chats", "event_id", event_id)
    if not event_chat:
        return False
    return updateEntry("event_chats", event_id, {"is_reminders_enabled": new_status})

def send_group_message_at_time(bot, group_id: str, message_thread_id: str, message: str, time: datetime):
    """Send a message to a group at a specific time"""
    # send message
    pass

def generate_reminder_message(event_id: str) -> str:
    """Generate a reminder message for an event"""
    event = getEvent(event_id)
    if not event:
        return ""
    
    # get confirmed duration
    confirmed_event_data = getConfirmedEvent(event_id)
    if not confirmed_event_data:
        return ""
    confirmed_start_time = confirmed_event_data['confirmed_start_time']
    confirmed_start_time_str = format_date_for_message(parse_date(confirmed_start_time)) + " " + format_time_from_iso(confirmed_start_time)
    confirmed_end_time = confirmed_event_data['confirmed_end_time']
    confirmed_end_time_str = format_date_for_message(parse_date(confirmed_end_time)) + " " + format_time_from_iso(confirmed_end_time)

    participants = generate_confirmed_event_participants_list(event_id)
    return f"Reminder: {event['event_name']} is happening on {confirmed_start_time_str} to {confirmed_end_time_str}!
        \n\nParticipants: {participants}"

def toggle_reminders(call: types.CallbackQuery, event_id: str, tele_id: str):
    """Toggle reminders for an event"""
    # get event
    event = getEvent(event_id)
    if not event:
        return False
    
    # get reminder status
    is_reminders_enabled = get_reminders_status(event_id)

    is_owner = check_ownership(event_id, tele_id)
    if not is_owner and is_reminders_enabled:
        bot.answer_callback_query(
            call.id,
            "You are not the owner of this event.",
            show_alert=False
        )
        return
    elif is_owner and is_reminders_enabled: # disable reminders
        update_reminders_status(event_id, False)
        bot.answer_callback_query(
            call.id,
            f"Reminders for event {event['event_name']} have been disabled.",
            show_alert=False
        )
    else: # enable reminders
        update_reminders_status(event_id, True)
        bot.answer_callback_query(
            call.id,
            f"Reminders for event {event['event_name']} have been enabled.",
            show_alert=False
        )