import telebot
from telebot import types
from datetime import datetime, time, timezone
from tzlocal import get_localzone

# Import from config
from ..config.config import bot
from ..services.database_service import getEntry, setEntry, updateEntry
from ..services.user_service import updateUsername, setUserSleepPreferences
from ..services.availability_service import getUserAvailability
from ..utils.message_templates import WELCOME_MESSAGE, HELP_MESSAGE
from ..utils.web_app import create_web_app_url
from urllib.parse import urlencode
import uuid

def register_command_handlers(bot):
    """Register all command-related handlers"""

    @bot.message_handler(commands=['start'])
    def send_welcome(message):
        if message.chat.type == 'private':
            db_result = getEntry("users", "tele_id", str(message.from_user.id))
            if db_result is None:
                print("User not found in DB, creating new entry.", message.from_user.id)
                setEntry("users", {
                    "uuid" : str(uuid.uuid4()),
                    "tele_id": str(message.from_user.id),
                    "tele_user": str(message.from_user.username),
                    "initialised": True,
                    "callout_cleared": True
                })
            else:
                if not db_result["initialised"]:
                    updateEntry("users", "tele_user", db_result["tele_user"], "initialised", True)
                    updateEntry("users", "tele_user", db_result["tele_user"], "callout_cleared", True)
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
