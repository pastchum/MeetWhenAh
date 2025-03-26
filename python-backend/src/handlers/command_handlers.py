from telebot import types
from datetime import datetime
from ..config.config import bot
from ..services.user_service import setEntry, getEntry, updateEntry, updateUsername
from ..services.availability_service import getUserAvailability, setUserSleepPreferences
from ..utils.message_templates import WELCOME_MESSAGE, HELP_MESSAGE
from ..utils.web_app import create_web_app_url
from urllib.parse import urlencode

@bot.message_handler(commands=['start'])
def send_welcome(message):
    if message.chat.type == 'private':
        db_result = getEntry("Users", "tele_id", str(message.from_user.id))
        if db_result is None:
            setEntry("Users", {
                "tele_id": str(message.from_user.id),
                "tele_user": str(message.from_user.username),
                "initialised": True,
                "callout_cleared": True
            })
        else:
            if not db_result.to_dict()["initialised"]:
                updateEntry(db_result, "initialised", True)
                updateEntry(db_result, "callout_cleared", True)

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
        sleep_start = message.text.strip()
        
        # Validate format (HHMM)
        if not (len(sleep_start) == 4 and sleep_start.isdigit()):
            raise ValueError("Invalid format")
            
        hours = int(sleep_start[:2])
        minutes = int(sleep_start[2:])
        
        if hours < 0 or hours > 23 or minutes < 0 or minutes > 59:
            raise ValueError("Invalid time")
            
        # Store temporarily
        user_id = message.from_user.id
        db_result = getEntry("Users", "tele_id", str(user_id))
        if not db_result:
            setEntry("Users", {
                "tele_id": str(user_id),
                "tele_user": str(message.from_user.username),
                "initialised": True,
                "callout_cleared": True,
                "temp_sleep_start": sleep_start
            })
        else:
            updateEntry(db_result, "temp_sleep_start", sleep_start)
            
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
        db_result = getEntry("Users", "tele_id", str(user_id))
        
        if not db_result or "temp_sleep_start" not in db_result.to_dict():
            bot.send_message(
                message.chat.id,
                "Something went wrong. Please try /sleep again."
            )
            return
            
        sleep_start = db_result.to_dict()["temp_sleep_start"]
        
        # Save to database
        setUserSleepPreferences(user_id, sleep_start, sleep_end)
        
        # Provide formatted times for confirmation
        start_formatted = f"{sleep_start[:2]}:{sleep_start[2:]}"
        end_formatted = f"{sleep_end[:2]}:{sleep_end[2:]}"
        
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