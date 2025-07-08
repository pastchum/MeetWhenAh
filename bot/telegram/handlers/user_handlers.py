import telebot
from telebot import types
import logging
from ..services.scheduling_service import DEFAULT_SLEEP_HOURS
from ..services.user_service import setUserSleepPreferences
from ..config.config import bot
from ..utils.message_templates import HELP_MESSAGE

logger = logging.getLogger(__name__)

def register_user_handlers(bot):
    """Register all user-related handlers"""
    
    @bot.message_handler(commands=['sleep'])
    def sleep_command(message):
        # This command only works in private chats
        if message.chat.type != 'private':
            bot.reply_to(message, "This command only works when you <i>private message</i> me!")
            return

        markup = types.ForceReply(selective=False)
        msg = bot.send_message(
            message.chat.id,
            "Please enter your sleep start time in 24-hour format (HHMM):\n"
            "For example, 2300 for 11:00 PM",
            reply_markup=markup
        )
        bot.register_next_step_handler(msg, process_sleep_start)

    def process_sleep_start(message):
        start_time = message.text.strip()
        
        # Validate time format
        if not start_time.isdigit() or len(start_time) != 4:
            markup = types.ForceReply(selective=False)
            msg = bot.send_message(
                message.chat.id,
                "Invalid format. Please enter time in HHMM format (e.g., 2300 for 11:00 PM):",
                reply_markup=markup
            )
            bot.register_next_step_handler(msg, process_sleep_start)
            return

        # Store start time and ask for end time
        markup = types.ForceReply(selective=False)
        msg = bot.send_message(
            message.chat.id,
            "Now, please enter your sleep end time in 24-hour format (HHMM):\n"
            "For example, 0700 for 7:00 AM",
            reply_markup=markup
        )
        bot.register_next_step_handler(msg, process_sleep_end, start_time)

    def process_sleep_end(message, start_time):
        end_time = message.text.strip()
        
        # Validate time format
        if not end_time.isdigit() or len(end_time) != 4:
            markup = types.ForceReply(selective=False)
            msg = bot.send_message(
                message.chat.id,
                "Invalid format. Please enter time in HHMM format (e.g., 0700 for 7:00 AM):",
                reply_markup=markup
            )
            bot.register_next_step_handler(msg, process_sleep_end, start_time)
            return

        # Store sleep preferences
        setUserSleepPreferences(message.from_user.id, start_time, end_time)
        bot.reply_to(
            message,
            f"Sleep preferences saved!\n"
            f"Start time: {start_time}\n"
            f"End time: {end_time}"
        ) 