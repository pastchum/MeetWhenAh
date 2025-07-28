import logging
from datetime import datetime, timezone, timedelta
import time

# Import from config
from telegram.config.config import bot

# Import from background scheduler
from background_scheduler.background_scheduler import add_cron_job, add_date_job, scheduler, remove_job

# Import from services
from .database_service import setEntry, updateEntry, getEntries, getEntry
from .user_service import getUser
from .event_service import getEvent, check_ownership, generate_confirmed_event_participants_list, getConfirmedEvent

# Import from other
import uuid
from telebot import types
from utils.message_templates import REMINDER_ON_MESSAGE, REMINDER_OFF_MESSAGE
from utils.date_utils import format_date_for_message, format_time_from_iso, parse_date

EVENT_REMINDER_HOUR_OFFSET = 2

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

def add_reminder_job(event_id: str, chat_id: str, thread_id: str, job_id: str):
    """Add a reminder job for an event"""
    return setEntry("event_reminders", event_id, {"chat_id": chat_id, "thread_id": thread_id, "job_id": job_id})

def remove_reminder_job(event_id: str, chat_id: str):
    """Remove a reminder job for an event"""
    event_reminders = getEntries("event_reminders", "event_id", event_id)
    if not event_reminders:
        return False
    for event_reminder in event_reminders:
        if event_reminder["chat_id"] == chat_id:
            remove_job(event_reminder["job_id"])
            return True
    return False

def send_group_message(group_id: str, message_thread_id: str, message: str):
    """Send a message to a group"""
    try:
        bot.send_message(chat_id=group_id, text=message, message_thread_id=message_thread_id)
    except Exception as e:
        logging.error(f"Error sending message to group {group_id}: {e}")

def send_group_message_at_time(group_id: str, message_thread_id: str, message: str, time: datetime):
    """Send a message to a group at a specific time"""
    # send message
    job = add_date_job(lambda: send_group_message(group_id, message_thread_id, message), time)
    return job

def send_daily_reminders():
    """Send daily reminders for all events"""
    reminder_events = getEntries("event_chats", "is_reminders_enabled", True)
    print("events from reminders: ", reminder_events)
    for event_chat in reminder_events:
        event_id = event_chat["event_id"]

        # check confirmed
        confirmed_event_data = getConfirmedEvent(event_id)
        if not confirmed_event_data:
            continue

        # check if event has passed
        confirmed_start_time = confirmed_event_data['confirmed_start_time']
        if parse_date(confirmed_start_time) < datetime.now(timezone.utc):
            continue

        message = generate_daily_reminder_message(event_id)
        
        send_group_message(event_chat["chat_id"], event_chat["thread_id"], message)

def send_event_reminder(event_id: str):
    """Send an event reminder at an offset from the confirmed start time"""
    event = getEvent(event_id)
    if not event:
        return
    event_chat = getEntry("event_chats", "event_id", event_id)
    if not event_chat:
        return
    
    # get confirmed duration
    confirmed_event_data = getConfirmedEvent(event_id)
    if not confirmed_event_data:
        return ""
    confirmed_start_time = confirmed_event_data['confirmed_start_time']
    # get reminder time
    reminder_time = parse_date(confirmed_start_time) - timedelta(hours=EVENT_REMINDER_HOUR_OFFSET)

    message = generate_event_reminder_message(event_id)
    job_id = send_group_message_at_time(event_chat["chat_id"], event_chat["thread_id"], message, reminder_time)
    return job_id

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

    return f"Reminder: {event['event_name']} is happening soon!\n\nParticipants:\n{participants}"

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
    confirmed_start_time_str = format_date_for_message(parse_date(confirmed_start_time)) + " " + format_time_from_iso(confirmed_start_time)
    confirmed_end_time = confirmed_event_data['confirmed_end_time']
    confirmed_end_time_str = format_date_for_message(parse_date(confirmed_end_time)) + " " + format_time_from_iso(confirmed_end_time)

    participants = generate_confirmed_event_participants_list(event_id)
    return f"Reminder: {event['event_name']} is happening on {confirmed_start_time_str} to {confirmed_end_time_str}!\n\nParticipants:\n{participants}"

def toggle_reminders(call: types.CallbackQuery, event_id: str, tele_id: str):
    """Toggle reminders for an event"""
    # get event
    event = getEvent(event_id)
    if not event:
        return False
    
    # get reminder status
    is_reminders_enabled = get_reminders_status(event_id)
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
        # remove job
        remove_reminder_job(event_id, event_chat["chat_id"])

        bot.answer_callback_query(
            call.id,
            f"Reminders for event {event['event_name']} have been disabled.",
            show_alert=False
        )
    else: # enable reminders
        update_reminders_status(event_id, True)
        # add job
        job_id = send_event_reminder(event_id)
        add_reminder_job(event_id, event_chat["chat_id"], event_chat["thread_id"], job_id)
        bot.answer_callback_query(
            call.id,
            f"Reminders for event {event['event_name']} have been enabled.",
            show_alert=False
        )

def main():
    send_daily_reminders()
    print("sending event reminder at time")
    send_event_reminder("9b8c611b-1b03-4a49-be85-e28df8f25788")
    for i in range(10):
        print("waiting for 1 second")
        time.sleep(1)
    print("done waiting")
    print(scheduler.get_jobs())
    print("done")

if __name__ == "__main__":
    main()