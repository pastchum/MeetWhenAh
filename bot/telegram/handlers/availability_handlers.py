import telebot
from telebot import types
import logging

# Import from config and utils
from ..config.config import bot
from ..utils.web_app import create_web_app_url

# Import from services
from services.availability_service import ask_availability
from services.event_service import getEvent, getUserAvailability, updateUserAvailability
from services.database_service import getEntry, setEntry, updateEntry

# Import from scheduler
from scheduler.scheduler import format_availability_summary

# Import from utils
from ..utils.message_templates import HELP_MESSAGE

logger = logging.getLogger(__name__)

def register_availability_handlers(bot):
    """Register all availability-related handlers"""
    
    @bot.message_handler(commands=['myavailability'])
    def my_availability(message):
        """Show user's availability for an event"""
        try:
            # Extract event ID from command arguments
            args = message.text.split()
            if len(args) < 2:
                bot.reply_to(message, "Please provide an event ID. Usage: /myavailability <event_id>")
                return
            
            event_id = args[1]
            username = message.from_user.username or str(message.from_user.id)
            
            # Get and format availability summary
            summary = format_availability_summary(event_id, username)
            bot.reply_to(message, summary)
            
        except Exception as e:
            logger.error(f"Error in my_availability handler: {str(e)}")
            bot.reply_to(message, "Failed to get your availability. Please try again later.")

    @bot.message_handler(commands=['updateavailability'])
    def update_availability(message):
        """Update user's availability for an event"""
        try:
            # Extract event ID from command arguments
            args = message.text.split()
            if len(args) < 2:
                bot.reply_to(message, "Please provide an event ID. Usage: /updateavailability <event_id>")
                return
            
            event_id = args[1]
            
            # Check if event exists
            event = getEvent(event_id)
            if not event:
                bot.reply_to(message, "Event not found")
                return
            
            # Create web app button for availability selection
            username = message.from_user.username or str(message.from_user.id)
            markup = types.InlineKeyboardMarkup()
            webapp_btn = types.InlineKeyboardButton(
                text="Select Availability",
                web_app=types.WebAppInfo(url=create_web_app_url("/dragselector", 1, event_id=event_id, username=username))
            )
            markup.add(webapp_btn)
            
            bot.reply_to(
                message,
                f"Please select your availability for {event['name']}:",
                reply_markup=markup
            )
            
        except Exception as e:
            logger.error(f"Error in update_availability handler: {str(e)}")
            bot.reply_to(message, "Failed to update availability. Please try again later.")

    return bot
