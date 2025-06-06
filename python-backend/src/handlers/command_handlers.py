from telebot import types
from datetime import datetime, time, timezone
from tzlocal import get_localzone

from ..config.config import bot
from ..services.database_service import getEntry, setEntry, updateEntry
from ..services.user_service import updateUsername, setUserSleepPreferences
from ..services.availability_service import getUserAvailability
from ..utils.message_templates import WELCOME_MESSAGE, HELP_MESSAGE
from ..utils.web_app import create_web_app_url
from urllib.parse import urlencode
import uuid

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
        bot.reply_to(message, WELCOME_MESSAGE)

@bot.message_handler(commands=['help'])
def help_command(message):
    bot.reply_to(message, HELP_MESSAGE)

@bot.message_handler(commands=['sleep'])
def sleep_command(message):
    if message.chat.type != 'private':
        bot.reply_to(message, "This command only works in private chat. Please message me directly.")
        return
        
    markup = types.ForceReply(selective=False)
    bot.send_message(
        message.chat.id, 
        "When do you usually go to sleep? Please enter in 24-hour format (e.g., 2300 for 11:00 PM):",
        reply_markup=markup
    )
    bot.register_next_step_handler(message, process_sleep_start)

def process_sleep_start(message):
    try:
        sleep_start_message = message.text.strip()
        
        # Validate format (HHMM)
        if not (len(sleep_start_message) == 4 and sleep_start_message.isdigit()):
            raise ValueError("Invalid format")
            
        hours = int(sleep_start_message[:2])
        minutes = int(sleep_start_message[2:])
        
        if hours < 0 or hours > 23 or minutes < 0 or minutes > 59:
            raise ValueError("Invalid time")
        
        # Get local timezone
        system_timezone = get_localzone()

        # Convert sleep_start into timetz format
        #TODO: fix timezone issue where it is not set to local timezone
        sleep_start_time = time(hour=hours, minute=minutes, tzinfo=system_timezone).isoformat()

        # Store temporarily
        user_id = message.from_user.id
        db_result = getEntry("users", "tele_id", str(user_id))
        if not db_result:
            setEntry("users", {
                "uuid" : str(uuid.uuid4()),
                "tele_id": str(message.from_user.id),
                "tele_user": str(message.from_user.username),
                "initialised": True,
                "callout_cleared": True,
                "sleep_start_time": sleep_start_time
            })
        else:
            updateEntry("users", "tele_id", user_id, "sleep_start_time", sleep_start_time)
            
        # Ask for wake up time
        markup = types.ForceReply(selective=False)
        bot.send_message(
            message.chat.id, 
            "When do you usually wake up? Please enter in 24-hour format (e.g., 0700 for 7:00 AM):",
            reply_markup=markup
        )
        bot.register_next_step_handler(message, process_sleep_end)
        
    except ValueError:
        bot.send_message(
            message.chat.id,
            "Invalid time format. Please use HHMM format (e.g., 2300 for 11:00 PM). Try /sleep again."
        )

def process_sleep_end(message):
    try:
        sleep_end = message.text.strip()
        
        # Validate format (HHMM)
        if not (len(sleep_end) == 4 and sleep_end.isdigit()):
            raise ValueError("Invalid format")
            
        hours = int(sleep_end[:2])
        minutes = int(sleep_end[2:])
        
        if hours < 0 or hours > 23 or minutes < 0 or minutes > 59:
            raise ValueError("Invalid time")
            
        # Get the temp sleep start time
        user_id = message.from_user.id
        db_result = getEntry("users", "tele_id", str(user_id))
        
        if not db_result or "sleep_start_time" not in db_result:
            bot.send_message(
                message.chat.id,
                "Something went wrong. Please try /sleep again."
            )
            return
        

                
        # Get local timezone
        system_timezone = get_localzone()

        # Convert sleep_end into timetz format
        #TODO: fix timezone issue where it is not set to local timezone
        sleep_end_time = time(hour=hours, minute=minutes, tzinfo=system_timezone).isoformat()

        sleep_start_time = db_result["sleep_start_time"]
        
        # Save to database
        setUserSleepPreferences(user_id, sleep_start_time, sleep_end_time)
        
        # Provide formatted times for confirmation
        start_formatted = f"{sleep_start_time[:5]}"
        end_formatted = f"{sleep_end_time[:5]}"
        
        bot.send_message(
            message.chat.id,
            f"Your sleep hours have been set: {start_formatted} to {end_formatted}.\n\n"
            f"These will be used to improve scheduling for your events!"
        )
        
    except ValueError:
        bot.send_message(
            message.chat.id,
            "Invalid time format. Please use HHMM format (e.g., 0700 for 7:00 AM). Try /sleep again."
        ) 