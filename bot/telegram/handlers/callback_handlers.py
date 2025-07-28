import telebot
from telebot import types
import logging

# Import from config
from ..config.config import bot

# Import from services
from services.event_service import (
    getEvent, 
    generate_event_description,
    getConfirmedEvent,
    generate_confirmed_event_description,
    generate_confirmed_event_participants_list,
    join_event,
    check_membership,
    leave_event,
    check_ownership
)
from services.user_service import (
    getUser,
    setUser,
    updateUserInitialised,
    updateUserCalloutCleared,
    updateUsername
)
from services.reminder_service import (
    toggle_reminders
)

# Import from utils
from utils.message_templates import HELP_MESSAGE

logger = logging.getLogger(__name__)

def register_callback_handlers(bot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith("join:"))
    def handle_join_callback(call):
        """Handle join event button clicks"""
        try:
            logger.info(f"Join callback data: {call}")
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
                    show_alert=False
                )
            else:
                join_event(event_id, tele_id)
                bot.answer_callback_query(
                    call.id,
                    f"{call.from_user.username} has joined the event.",
                    show_alert=False
                )
        except Exception as e:
            logger.error(f"Error in join callback handler: {str(e)}")
            bot.answer_callback_query(
                call.id,
                "An error occurred. Please try again later.",
                show_alert=True
            )

    @bot.callback_query_handler(func=lambda call: call.data.startswith("reminders:"))
    def handle_reminders_callback(call):
        """Handle reminders button clicks"""
        try:
            event_id = call.data.split(":")[1]
            tele_id = call.from_user.id
            user_data = getUser(tele_id)
            tele_user = call.from_user.username

            is_owner = check_ownership(event_id, tele_id)
            if not is_owner:
                bot.answer_callback_query(
                    call.id,
                    "You are not the owner of this event.",
                    show_alert=True
                )
                return
            
            # toggle reminders
            toggle_reminders(message=call.message, event_id=event_id)
        except Exception as e:
            logger.error(f"Error in reminders callback handler: {str(e)}")
            bot.answer_callback_query(
                call.id,
                "An error occurred. Please try again later.",
                show_alert=True
            )