import telebot
from telebot import types
from datetime import datetime, time, timezone
from tzlocal import get_localzone

# Import from services
from services.database_service import getEntry, setEntry, updateEntry
from services.user_service import (
    updateUsername,
    setUserSleepPreferences,
    getUser,
    setUser,
    updateUserInitialised,
    updateUserCalloutCleared
)
from services.share_service import put_ctx

# Import from utils
from utils.message_templates import WELCOME_MESSAGE, HELP_MESSAGE

# Import from other
from urllib.parse import urlencode
import uuid

def register_welcome_handlers(bot):
    """Register all command-related handlers"""
    
    @bot.message_handler(commands=['help'])
    def help_command(message):
        # Generate share token for dashboard access
        chat_id = message.chat.id
        thread_id = getattr(message, "message_thread_id", None)
        user_id = message.from_user.id
        placeholder_message_id = 0
        
        token = put_ctx(user_id, chat_id, placeholder_message_id, thread_id)
        
        # Create dashboard button
        markup = types.InlineKeyboardMarkup()
        params = f"dashboard={token}"
        mini_app_url = f"https://t.me/{bot.get_me().username}/meetwhenah?startapp={params}"
        
        dashboard_btn = types.InlineKeyboardButton(
            text="Open Dashboard",
            url=mini_app_url
        )
        markup.add(dashboard_btn)
        
        if message.chat.type == 'private':
            bot.reply_to(message, HELP_MESSAGE, reply_markup=markup)
        else:
            # In group chat, send help message without replying to the user's message
            bot.send_message(message.chat.id, HELP_MESSAGE, reply_markup=markup)
