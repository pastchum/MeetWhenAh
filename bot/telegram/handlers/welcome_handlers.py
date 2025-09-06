import telebot
from telebot import types
from datetime import datetime, time, timezone
from tzlocal import get_localzone
import logging

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

logger = logging.getLogger(__name__)

def register_welcome_handlers(bot):
    """Register all command-related handlers"""
    
    @bot.message_handler(commands=['help'])
    def help_command(message):
        # Enhanced logging for help command
        user_info = {
            'user_id': message.from_user.id,
            'username': message.from_user.username,
            'first_name': message.from_user.first_name,
            'chat_type': message.chat.type,
            'chat_id': message.chat.id
        }
        
        logger.info(f"🚀 Help command triggered by user: {user_info}")
        print(f"🚀 Help command triggered by user: {user_info}")
        
        # Generate share token for dashboard access (similar to /share command)
        chat_id = message.chat.id
        thread_id = getattr(message, "message_thread_id", None)
        user_id = message.from_user.id
        
        # We'll use a placeholder message_id since this is for dashboard access, not message editing
        placeholder_message_id = 0
        
        token = put_ctx(user_id, chat_id, placeholder_message_id, thread_id)
        
        # Log the generated token
        logger.info(f"🔑 Generated share token for dashboard: {token}")
        print(f"🔑 Generated share token for dashboard: {token}")
        logger.info(f"🔑 Token context - user_id: {user_id}, chat_id: {chat_id}, thread_id: {thread_id}")
        print(f"🔑 Token context - user_id: {user_id}, chat_id: {chat_id}, thread_id: {thread_id}")
        
        # Create dashboard button using the same pattern as create button
        # This works in both private and group chats
        markup = types.InlineKeyboardMarkup()
        
        # Use the same URL pattern as create button
        params = f"dashboard={token}"
        mini_app_url = f"https://t.me/{bot.get_me().username}/meetwhenah?startapp={params}"
        
        dashboard_btn = types.InlineKeyboardButton(
            text="Open Dashboard",
            url=mini_app_url
        )
        markup.add(dashboard_btn)
        
        # Log the button creation
        logger.info(f"🔘 Created dashboard button with URL: {mini_app_url}")
        print(f"🔘 Created dashboard button with URL: {mini_app_url}")
        
        if message.chat.type == 'private':
            bot.reply_to(message, HELP_MESSAGE, reply_markup=markup)
            logger.info(f"📤 Sent help message to private chat for user {message.from_user.id}")
            print(f"📤 Sent help message to private chat for user {message.from_user.id}")
        else:
            # In group chat, mention the user who requested help
            help_text = f"@{message.from_user.username or message.from_user.first_name}, here's how to use the bot:\n\n{HELP_MESSAGE}"
            bot.send_message(message.chat.id, help_text, reply_markup=markup)
            logger.info(f"📤 Sent help message to group chat {message.chat.id} for user {message.from_user.id}")
            print(f"📤 Sent help message to group chat {message.chat.id} for user {message.from_user.id}")