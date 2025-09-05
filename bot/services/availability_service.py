import telebot
from telebot import types
import logging
from urllib.parse import quote
from collections import defaultdict

# Import bot config
from telegram.config.config import bot

# Import from events
from events.events import Event
from events.confirmed_events import ConfirmedEvent

# Import from services
from .database_service import getEntry, setEntry, updateEntry
from .event_service import (
    getEvent, 
    getUserAvailability, 
    updateUserAvailability, 
 getConfirmedEvent, 
    generate_confirmed_event_description,
    generate_event_description,
    generate_confirmed_event_participants_list
)

# Import from utils
from utils.message_templates import HELP_MESSAGE, AVAILABILITY_SELECTION
from utils.web_app import create_web_app_url

logger = logging.getLogger(__name__)

def ask_availability(chat_id: int, event_id: str, thread_id: int = None):
    """Ask user to provide availability for an event"""
    try:
        # Get event details
        event = Event.from_database(event_id)
        if not event:
            bot.send_message(chat_id=chat_id, message_thread_id=thread_id, text="Event not found")
            return
            
        markup = event.get_event_button()

        # generate event description
        event_description = event.get_event_details_for_message()

        text = AVAILABILITY_SELECTION.format(
            event_description=event_description,
            event_name=event.get_event_name()
        )

        bot.send_message(
            chat_id=chat_id,
            message_thread_id=thread_id,
            text=text,
            reply_markup=markup,
        )
        
    except Exception as e:
        logger.error(f"Error in ask_availability: {str(e)}")
        bot.send_message(chat_id=chat_id, message_thread_id=thread_id, text="Failed to set up availability selection. Please try again later.")

def ask_join(chat_id: int, event_id: str, thread_id: int = None):
    """Ask user to join an event"""
    try:
        # Get event details
        event = ConfirmedEvent.from_database(event_id)
        if not event:
            bot.send_message(chat_id=chat_id, message_thread_id=thread_id, text="Event not found")
            return None
        
        # generate event description with truncated description
        event_description = event.get_event_details_for_message()
        
        # create full message with participants
        rows = event.get_all_users_for_event() or []
        participant_count = len(rows)
        participants_formatted = "\n".join(
            f"• {row.get('user_uuid')} {row.get('emoji_icon', '')}".strip()
            for row in rows
        ) or "No participants yet"

        full_message = f"{event_description}\n\n👥 <b>Participants ({participant_count})</b>:\n{participants_formatted}"
        
        # add join button
        markup = event.get_event_button()

        # send event description and return message ID
        sent_message = bot.send_message(chat_id=chat_id, message_thread_id=thread_id, text=full_message, reply_markup=markup)
        return sent_message.message_id
    except Exception as e:
        logger.error(f"Error in ask_join: {str(e)}")
        bot.send_message(chat_id=chat_id, message_thread_id=thread_id, text="Failed to ask user to join event. Please try again later.")
        return None

def update_join_message(chat_id: int, message_id: int, event_id: str, thread_id: int = None):
    """Update the join message with current participant list"""
    try:
        # Get event details
        event = ConfirmedEvent.from_database(event_id)
        if not event:
            return False
        
        # generate event description with truncated description
        event_description = event.get_event_details_for_message()
        
        # create full message with participants
        rows = event.get_all_users_for_event() or []
        participant_count = len(rows)
        participants_formatted = "\n".join(
            f"• @{row.get('tele_user')} {row.get('emoji_icon', '')}".strip()
            for row in rows
        ) or "No participants yet"

        full_message = f"{event_description}\n\n👥 <b>Participants ({participant_count})</b>:\n{participants_formatted}"
        
        markup = event.get_event_button()

        # update the existing message
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=full_message,
            reply_markup=markup
        )
        return True
    except Exception as e:
        logger.error(f"Error updating join message: {str(e)}")
        return False

def format_availability_summary(event_id: str, username: str) -> str:
    """Format a summary of a user's availability for an event"""
    event = getEvent(event_id)
    if not event:
        return "Event not found"
    
    availability = getEntry("availability", "event_id", event_id)
    if not availability or username not in availability:
        return "No availability data found"
    
    user_availability = availability[username]
    if not user_availability:
        return "No availability data found"
    
    # Format the summary
    summary = f"Your availability for {event['event_name']}:\n\n"
    
    # Group availability by date
    by_date = defaultdict(list)
    for slot in user_availability:
        date = slot['date']
        time = f"{slot['start_time']}-{slot['end_time']}"
        by_date[date].append(time)
    
    # Format each date's availability
    for date in sorted(by_date.keys()):
        summary += f"{date}:\n"
        for time in sorted(by_date[date]):
            summary += f"  {time}\n"
        summary += "\n"
    
    return summary 