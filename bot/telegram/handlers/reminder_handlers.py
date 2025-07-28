import os
import json
from datetime import datetime, timedelta
import uuid
import telebot
from telebot import types

# Import from config
from ..config.config import bot



# Import from services
from services.user_service import updateUsername, getUser

# Import from utils
from utils.date_utils import daterange, parse_date, format_date_for_message, format_date

def register_reminder_handlers(bot):
    """Register all reminder handlers"""
    
    def handle_toggle_reminders(message):
        """Handle toggle reminders command"""
        chat_id = message.chat.id
        message_id = message.message_id
        user_id = message.from_user.id
        user_data = getUser(user_id)

        bot.delete_message(chat_id=chat_id, message_id=message_id)
        