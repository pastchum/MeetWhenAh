import telebot
from telebot import types
import logging

# Import from config and services
from ..config.config import bot
from ..services.database_service import getEntry, setEntry, updateEntry
from ..services.scheduling_service import format_availability_summary
from ..utils.web_app import create_web_app_url
from ..services.event_service import getEvent, getUserAvailability, updateUserAvailability
from ..utils.message_templates import HELP_MESSAGE
#from ..utils.native_interface import create_native_availability_selector, handle_native_availability_callback

logger = logging.getLogger(__name__)

def ask_availability(chat_id: int, event_id: str, username: str = None, group: bool = False):
    """Ask user to provide availability for an event"""
    try:
        # Get event details
        event = getEvent(event_id)
        if not event:
            bot.send_message(chat_id, "Event not found")
            return
        
        # private chat logic
        if not group: 
            # Create web app button for availability selection
            if username:
                web_app_url = create_web_app_url("/dragselector", 1, event_id=event_id, username=username)
            else:
                # Fallback for when username is not provided
                web_app_url = create_web_app_url("/dragselector", 1, event_id=event_id)
                
            markup = types.InlineKeyboardMarkup()
            webapp_btn = types.InlineKeyboardButton(
                text="Select Availability",
                web_app=types.WebAppInfo(url=web_app_url)
            )
            markup.add(webapp_btn)
            
            bot.send_message(
                chat_id,
                f"Please select your availability for {event['event_name']}:",
                reply_markup=markup
            )
        # group chat logic
        else: 
            miniapp_url = f"https://t.me/{bot.get_me().username}/MeetWhenAh?startapp=dragselector&event_id={event_id}"

            markup = types.InlineKeyboardMarkup()
            miniapp_btn = types.InlineKeyboardButton(
                text="Select Availability",
                url=miniapp_url
            )
            markup.add(miniapp_btn)

            bot.send_message(
                chat_id,
                f"Please select your availability for {event['event_name']}:",
                reply_markup=markup,
            )
        
    except Exception as e:
        logger.error(f"Error in ask_availability: {str(e)}")
        bot.send_message(chat_id, "Failed to set up availability selection. Please try again later.")
