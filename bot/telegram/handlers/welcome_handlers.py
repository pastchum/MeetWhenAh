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

# Import from utils
from utils.message_templates import WELCOME_MESSAGE, HELP_MESSAGE
from utils.web_app import create_web_app_url

# Import from other
from urllib.parse import urlencode
import uuid

def register_welcome_handlers(bot):
    """Register all command-related handlers"""
    
    @bot.message_handler(commands=['help'])
    def help_command(message):
        bot.reply_to(message, HELP_MESSAGE)
