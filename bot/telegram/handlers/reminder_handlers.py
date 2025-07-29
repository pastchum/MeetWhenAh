import os
import json
from datetime import datetime, timedelta
import uuid
import telebot
from telebot import types
import logging

logger = logging.getLogger(__name__)

# Import from config
from ..config.config import bot

# Import from services
from services.reminder_service import toggle_reminders

# Import from utils
from utils.date_utils import daterange, parse_date, format_date_for_message, format_date

def register_reminder_handlers(bot):
    """Register all reminder handlers"""    
    @bot.callback_query_handler(func=lambda call: call.data.startswith("reminders:"))
    def handle_reminders_callback(call):
        """Handle reminders button clicks"""
        try:
            event_id = call.data.split(":")[1]
            tele_id = call.from_user.id
            
            # toggle reminders
            toggle_reminders(call=call, event_id=event_id, tele_id=tele_id)
        except Exception as e:
            logger.error(f"Error in reminders callback handler: {str(e)}")
            bot.answer_callback_query(
                call.id,
                "An error occurred. Please try again later.",
                show_alert=True
            )