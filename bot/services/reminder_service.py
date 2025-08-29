import logging
from datetime import datetime, timezone, timedelta
import time

# Import from config
from telegram.config.config import bot

# Import from services
from .database_service import setEntry, updateEntry, getEntries, getEntry, supabase
from .user_service import getUser
from .event_service import getEvent, check_ownership, generate_confirmed_event_participants_list, getConfirmedEvent

# Import from other
import uuid
from telebot import types
from utils.message_templates import REMINDER_ON_MESSAGE, REMINDER_OFF_MESSAGE
from utils.date_utils import format_date_for_message, format_time_from_iso, parse_date, format_date_month_day, format_time_from_iso_am_pm

EVENT_REMINDER_HOUR_OFFSET = 2

def get_reminders_status(event_id: str) -> bool:
    """Get the reminder status for an event"""
    event = getEvent(event_id)
    if not event:
        return False
    return event["is_reminders_enabled"]

def update_reminders_status(event_id: str, new_status: bool):
    """Enable reminders for an event"""
    event = getEvent(event_id)
    if not event:
        return False
    return updateEntry("events", event_id, {"is_reminders_enabled": new_status})

def send_group_message(group_id: str, message_thread_id: str, message: str):
    """Send a message to a group"""
    try:
        bot.send_message(chat_id=group_id, text=message, message_thread_id=message_thread_id)
    except Exception as e:
        logging.error(f"Error sending message to group {group_id}: {e}")

def send_daily_availability_reminders():
    """Send daily availability reminders for all events"""
    response = supabase.rpc("get_unconfirmed_active_events_at_noon_local_time").execute()
    events = response.data
    print("events", events)
    for event in events:
        event_id = event["event_id"]
        event_chats = getEntries("event_chats", "event_id", event_id)
        if not event_chats:
            continue
        for event_chat in event_chats:
            message = generate_availability_reminder_message(event_id)
            send_group_message(event_chat["chat_id"], event_chat["thread_id"], message)

    print("done sending daily availability reminders")
    return True

def send_daily_event_reminders():
    """Send daily reminders for all events"""
    response = supabase.rpc("get_confirmed_events_at_local_noon").execute()
    events = response.data
    print("events", events)
    for event in events:
        event_id = event["event_id"]
        message = generate_event_reminder_message(event_id)
        # check confirmed
        confirmed_event_data = getConfirmedEvent(event_id)
        if not confirmed_event_data:
            continue
        # check if event has passed
        confirmed_start_time = confirmed_event_data['confirmed_start_time']
        if parse_date(confirmed_start_time) < datetime.now(timezone.utc):
            continue
        
        event_chats = getEntries("event_chats", "event_id", event_id)
        if not event_chats:
            continue
        for event_chat in event_chats:
            send_group_message(event_chat["chat_id"], event_chat["thread_id"], message)

    print("done sending daily event reminders")
    return True

def send_upcoming_event_reminders():
    """Send upcoming event reminders for all events"""
    response = supabase.rpc("get_confirmed_events_starting_soon").execute()
    events = response.data
    print("events", events)
    for event in events:
        event_id = event["event_id"]
        event_chats = getEntries("event_chats", "event_id", event_id)
        if not event_chats:
            continue
        for event_chat in event_chats:
            message = generate_event_reminder_message(event_id)
            send_group_message(event_chat["chat_id"], event_chat["thread_id"], message)

    print("done sending upcoming event reminders")
    return True

def send_event_reminder(event_id: str):
    """Send an event reminder at an offset from the confirmed start time"""
    event_chat = getEntry("event_chats", "event_id", event_id)
    if not event_chat:
        return

    message = generate_event_reminder_message(event_id)
    send_group_message(event_chat["chat_id"], event_chat["thread_id"], message)

def generate_availability_reminder_message(event_id: str) -> str:
    """Generate a reminder message to input availability"""
    event = getEvent(event_id)
    if not event:
        return ""
    
    # Format dates
    start_date = parse_date(event['start_date'])
    end_date = parse_date(event['end_date'])
    start_date_str = format_date_month_day(start_date)
    end_date_str = format_date_month_day(end_date)
    
    return f"""❓ **Reminder**: Please input your availability for the event

📅 **Event**: **{event['event_name']}**
⏰ **Date Range**: {start_date_str} - {end_date_str}"""

def generate_event_reminder_message(event_id: str) -> str:
    """Generate a reminder message for an event"""
    event = getEvent(event_id)
    if not event:
        return ""
    
    # get confirmed duration
    confirmed_event_data = getConfirmedEvent(event_id)
    if not confirmed_event_data:
        return ""

    participants = generate_confirmed_event_participants_list(event_id)

    return f"""❗ **Reminder**: **{event['event_name']}** is happening soon!

👥 **Participants**:
{participants}"""

def generate_daily_reminder_message(event_id: str) -> str:
    """Generate a reminder message for an event"""
    event = getEvent(event_id)
    if not event:
        return ""
    
    # get confirmed duration
    confirmed_event_data = getConfirmedEvent(event_id)
    if not confirmed_event_data:
        return ""
    confirmed_start_time = confirmed_event_data['confirmed_start_time']
    confirmed_start_time_str = format_date_month_day(parse_date(confirmed_start_time)) + " " + format_time_from_iso_am_pm(confirmed_start_time)
    confirmed_end_time = confirmed_event_data['confirmed_end_time']
    confirmed_end_time_str = format_date_month_day(parse_date(confirmed_end_time)) + " " + format_time_from_iso_am_pm(confirmed_end_time)

    participants = generate_confirmed_event_participants_list(event_id)
    return f"""❗ **Reminder**: **{event['event_name']}** is happening on {confirmed_start_time_str} to {confirmed_end_time_str}!

👥 **Participants**:
{participants}"""

def toggle_reminders(call: types.CallbackQuery, event_id: str, tele_id: str):
    """Toggle reminders for an event"""
    # get event
    event = getEvent(event_id)
    if not event:
        return False
    
    # get reminder status
    is_reminders_enabled = event["is_reminders_enabled"]
    event_chat = getEntry("event_chats", "event_id", event_id)
    if not event_chat:
        return False

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
        # add job
        bot.answer_callback_query(
            call.id,
            f"Reminders for event {event['event_name']} have been enabled.",
            show_alert=False
        )
