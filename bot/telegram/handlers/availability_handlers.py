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

def register_availability_handlers(bot):
    """Register all availability-related handlers"""
    
    @bot.message_handler(commands=['/myavailability'])
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

    @bot.message_handler(commands=['/updateavailability'])
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
            markup = types.InlineKeyboardMarkup()
            webapp_btn = types.InlineKeyboardButton(
                text="Select Availability",
                web_app=types.WebAppInfo(url=create_web_app_url(2, {"event_id": event_id}))
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

def ask_availability(chat_id: int, event_id: str):
    """Ask user to provide availability for an event"""
    try:
        # Get event details
        event = getEvent(event_id)
        if not event:
            bot.send_message(chat_id, "Event not found")
            return
        
        # Create web app button for availability selection
        markup = types.InlineKeyboardMarkup()
        webapp_btn = types.InlineKeyboardButton(
            text="Select Availability",
            web_app=types.WebAppInfo(url=create_web_app_url(2, {"event_id": event_id}))
        )
        markup.add(webapp_btn)
        
        bot.send_message(
            chat_id,
            f"Please select your availability for {event['name']}:",
            reply_markup=markup
        )
        
    except Exception as e:
        logger.error(f"Error in ask_availability: {str(e)}")
        bot.send_message(chat_id, "Failed to set up availability selection. Please try again later.")

@bot.callback_query_handler(func=lambda call: call.data.startswith(('slot_', 'save_', 'cancel_', 'date_')))
def handle_availability_callback(call):
    """Handle callbacks from the native availability selector."""
    handle_native_availability_callback(bot, call)

def get_user_events(user_id):
    """Get all events that a user is a member of."""
    try:
        events = []
        from ..services.user_service import supabase_client
        
        # Query events where user is a member
        event_data = supabase_client.from_('events').select('*').filter('members', 'cs', str(user_id)).execute()
        
        for event_data in event_data['data']:
            events.append({
                'id': event_data.get('event_id'),
                'name': event_data.get('event_name', 'Unnamed Event')
            })
            
        return events
    except Exception as e:
        print(f"Error getting user events: {e}")
        return [] 