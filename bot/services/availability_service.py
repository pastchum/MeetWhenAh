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
    generate_event_description
)

# Import from utils
from utils.message_templates import HELP_MESSAGE, AVAILABILITY_SELECTION
from utils.web_app import create_web_app_url

logger = logging.getLogger(__name__)

def ask_availability(chat_id: int, event_id: str, thread_id: int = None):
    """Ask user to provide availability for an event"""
    try:
        # Get event details
        event = getEvent(event_id)
        if not event:
            bot.send_message(chat_id=chat_id, message_thread_id=thread_id, text="Event not found")
            return
        
        params = f"dragselector={event_id}"
        miniapp_url = f"https://t.me/{bot.get_me().username}/meetwhenah?startapp={params}"

        markup = types.InlineKeyboardMarkup()
        miniapp_btn = types.InlineKeyboardButton(
            text="Select Availability",
            url=miniapp_url
        )
        markup.add(miniapp_btn)

        # generate event description
        event_description = generate_event_description(event)

        text = AVAILABILITY_SELECTION.format(
            event_description=event_description,
            event_name=event['event_name']
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
        event = Event.from_database(event_id)
        if not event:
            bot.send_message(chat_id=chat_id, message_thread_id=thread_id, text="Event not found")
            return
        
        # generate event description
        event_description = event.get_event_details_for_message()
        
        # add join button
        markup = event.get_event_button()

        # send event description
        bot.send_message(chat_id=chat_id, message_thread_id=thread_id, text=event_description, reply_markup=markup)
    except Exception as e:
        logger.error(f"Error in ask_join: {str(e)}")
        bot.send_message(chat_id=chat_id, message_thread_id=thread_id, text="Failed to ask user to join event. Please try again later.")

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
    summary = f"Your availability for {event['name']}:\n\n"
    
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