from telebot import types
import logging

# Import from config
from ..config.config import bot

# Import from services
from services.event_service import (
    getEvent, 
    getConfirmedEvent, 
    generate_confirmed_event_description, 
    generate_confirmed_event_participants_list,
    set_chat
)
from services.availability_service import ask_availability, send_confirmed_event_availability

# Import from other
import uuid

logger = logging.getLogger(__name__)

bot_username = bot.get_me().username
print(f"Bot username: {bot_username}")

def register_share_handlers(bot):
    """Register all share handlers"""

    @bot.message_handler(func=lambda message: message.text.lower().startswith(f"@{bot_username}".lower()))
    def handle_share(message):
        """Handle share command"""

        try:
            # get message details
            message_id = message.id
            chat_id = message.chat.id
            user_id = message.from_user.id
            thread_id = message.message_thread_id
            event_id = message.text.split(" ")[1]

            # delete message    
            #bot.delete_message(chat_id=chat_id, message_id=message_id)

            # set chat
            set_chat(event_id=event_id, chat_id=chat_id, thread_id=thread_id)

            # get event id
            logger.info(f"Sharing event {event_id}")

            
            event = getEvent(event_id)
            if not event:
                bot.send_message(message.chat.id, "Event not found. Please create an event first.")
                return
            
            # check if event is confirmed
            confirmed_event = getConfirmedEvent(event_id)
            if not confirmed_event:
                # handle availability selection
                logger.info(f"Event not confirmed. Availability is not yet set.")
                ask_availability(chat_id=chat_id, thread_id=thread_id, event_id=event_id)
                return
            
            # handle confirmed event
            send_confirmed_event_availability(event_id=event_id, chat_id=chat_id, thread_id=thread_id)
        except Exception as e:
            logger.error(f"Error sharing event: {e}")
            bot.send_message(chat_id=chat_id, message_thread_id=thread_id, text="Failed to share event. Please try again later.")