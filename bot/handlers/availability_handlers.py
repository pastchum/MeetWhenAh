from telebot import types
import logging
from ..services.scheduling_service import calculate_optimal_meeting_time

logger = logging.getLogger(__name__)

def register_availability_handlers(bot):
    """Register all availability-related handlers"""
    
    @bot.message_handler(commands=['myavailability'])
    def check_availability(message):
        if message.chat.type != 'private':
            bot.reply_to(message, "This command only works when you <i>private message</i> me!")
            return

        markup = types.ForceReply(selective=False)
        msg = bot.send_message(
            message.chat.id,
            "Please enter the event ID to check your availability:",
            reply_markup=markup
        )
        bot.register_next_step_handler(msg, process_check_availability)

    def process_check_availability(message):
        event_id = message.text.strip()
        
        # Get availability from database
        # This will be implemented in the next step
        bot.reply_to(
            message,
            f"Checking availability for event {event_id}..."
        )

    @bot.message_handler(commands=['updateavailability'])
    def update_availability(message):
        if message.chat.type != 'private':
            bot.reply_to(message, "This command only works when you <i>private message</i> me!")
            return

        markup = types.ForceReply(selective=False)
        msg = bot.send_message(
            message.chat.id,
            "Please enter the event ID to update your availability:",
            reply_markup=markup
        )
        bot.register_next_step_handler(msg, process_update_availability)

    def process_update_availability(message):
        event_id = message.text.strip()
        
        # Update availability in database
        # This will be implemented in the next step
        bot.reply_to(
            message,
            f"Updating availability for event {event_id}..."
        ) 