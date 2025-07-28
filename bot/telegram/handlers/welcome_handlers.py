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

    @bot.message_handler(commands=['start'])
    def send_welcome(message):
        if message.chat.type == 'private':
            tele_id = str(message.from_user.id)
            db_result = getUser(tele_id)
            if db_result is None:
                print("User not found in DB, creating new entry.", message.from_user.id)
                username = str(message.from_user.username)
                setUser(tele_id, username)
            else:
                if not db_result["initialised"]:
                    updateUserInitialised(tele_id)
                    updateUserCalloutCleared(tele_id)
                if db_result["tele_user"] != str(message.from_user.username):
                    print("Username changed, updating in DB.")
                    updateUsername(message.from_user.id, message.from_user.username)

            # Create web app URL for datepicker
            web_app_url = create_web_app_url(
                path='/datepicker',
                web_app_number=0  # 0 for create event
            )
            
            markup = types.ReplyKeyboardMarkup(row_width=1)
            web_app_info = types.WebAppInfo(url=web_app_url)
            web_app_button = types.KeyboardButton(text="Create Event", web_app=web_app_info)
            markup.add(web_app_button)

            bot.reply_to(message, WELCOME_MESSAGE, reply_markup=markup)
        else:
            # In group chat, provide instructions to message the bot privately
            welcome_text = "To create an event, please message me privately!"
            markup = None
            bot.send_message(message.chat.id, welcome_text, reply_markup=markup)

    @bot.message_handler(commands=['help'])
    def help_command(message):
        bot.reply_to(message, HELP_MESSAGE)
