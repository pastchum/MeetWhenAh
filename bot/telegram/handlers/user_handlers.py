import telebot
from telebot import types
import logging

# Import from config
from ..config.config import bot

# Import from best time algo
from best_time_algo.best_time_algo import DEFAULT_SLEEP_HOURS

# Import from services
from services.user_service import setUserSleepPreferences, setUser, updateUserInitialised, updateUserCalloutCleared, updateUsername, getUser
from services.event_service import check_membership, join_event, leave_event
from services.availability_service import update_join_message

# Import from utils
from utils.message_templates import (
    HELP_MESSAGE, 
    SLEEP_START_PROMPT, 
    SLEEP_END_PROMPT, 
    SLEEP_INVALID_FORMAT
)

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
            "😴 <b>Sleep Schedule Setup</b>\n\nPlease enter your sleep start time in 24-hour format (HHMM):\n"
            "For example, 2300 for 11:00 PM",
            reply_markup=markup
        )
        bot.register_next_step_handler(msg, process_sleep_start)


    @bot.callback_query_handler(func=lambda call: call.data.startswith("join:"))
    def handle_join_callback(call):
        """Handle join event button clicks"""
        try:
            event_id = call.data.split(":")[1]
            tele_id = call.from_user.id
            user_data = getUser(tele_id)
            tele_user = call.from_user.username
            if not user_data:
                success = setUser(tele_id, tele_user)
                if not success:
                    logger.error(f"Error setting user: {str(e)}")
                    bot.answer_callback_query(
                        call.id,
                        "An error occurred. Please try again later.",
                        show_alert=True
                    )
                    return
                updateUserInitialised(tele_id)
                updateUserCalloutCleared(tele_id)
            
            # update username if necessary
            if user_data["tele_user"] != tele_user:
                updateUsername(tele_id, tele_user)

            # Check if user is already a member of the event
            membership_status = check_membership(event_id, tele_id)
            if membership_status:
                leave_event(event_id, tele_id)
                bot.answer_callback_query(
                    call.id,
                    f"{call.from_user.username} has left the event.",
                    show_alert=True
                )
            else:
                join_event(event_id, tele_id)
                bot.answer_callback_query(
                    call.id,
                    f"{call.from_user.username} has joined the event.",
                    show_alert=True
                )
            
            # Update the join message
            message_id = call.message.message_id
            chat_id = call.message.chat.id
            thread_id = call.message.message_thread_id
            update_join_message(
                chat_id=chat_id,
                message_id=message_id,
                event_id=event_id,
                thread_id=thread_id
            )
        except Exception as e:
            logger.error(f"Error in join callback handler: {str(e)}")
            bot.answer_callback_query(
                call.id,
                "An error occurred. Please try again later.",
                show_alert=True
            )

    def process_sleep_start(message):
        start_time = message.text.strip()
        
        # Validate time format
        if not start_time.isdigit() or len(start_time) != 4:
            markup = types.ForceReply(selective=False)
            msg = bot.send_message(
                message.chat.id,
                "❌ <b>Invalid Format</b>\n\nPlease enter time in HHMM format (e.g., 2300 for 11:00 PM):",
                reply_markup=markup
            )
            bot.register_next_step_handler(msg, process_sleep_start)
            return

        # Store start time and ask for end time
        markup = types.ForceReply(selective=False)
        msg = bot.send_message(
            message.chat.id,
            "😴 <b>Sleep Schedule Setup</b>\n\nNow, please enter your sleep end time in 24-hour format (HHMM):\n"
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
                "❌ <b>Invalid Format</b>\n\nPlease enter time in HHMM format (e.g., 0700 for 7:00 AM):",
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
