from telebot import types
import json
import random
import string
from datetime import datetime, timedelta
from ..config.config import bot
from ..services.user_service import getEntry, setEntry, updateEntry
from ..services.event_service import getEventSleepPreferences
from ..services.scheduling_service import calculate_optimal_meeting_time
from ..utils.web_app import create_web_app_url
from ..utils.date_utils import daterange
from ..handlers.availability_handlers import ask_availability

# Keep track of processed message IDs to prevent duplicate processing
processed_messages = set()

@bot.message_handler(content_types=['web_app_data'])
def handle_webapp(message):
    """Handle web app data with proper error handling and state clearing."""
    try:
        # Check if we've already processed this message
        if message.message_id in processed_messages:
            return
        processed_messages.add(message.message_id)
        
        # Keep set size manageable
        if len(processed_messages) > 1000:
            processed_messages.clear()
        
        # Clear any pending next step handlers
        #bot.clear_step_handler_by_chat_id(message.chat.id)
        
        if not hasattr(message, 'web_app_data') or not message.web_app_data:
            bot.send_message(message.chat.id, "Invalid web app data received.")
            return
            
        try:
            web_app_data = json.loads(message.web_app_data.data)
            print(f"Received web app data: {web_app_data}")  # Debug log
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")  # Debug log
            bot.send_message(message.chat.id, "Invalid data format received.")
            return
            
        if 'web_app_number' not in web_app_data:
            print("Missing web_app_number in data")  # Debug log
            bot.send_message(message.chat.id, "Missing required data.")
            return
            
        web_app_number = web_app_data.get("web_app_number")
        print(f"Processing web_app_number: {web_app_number}")  # Debug log
        
        if web_app_number == 0:
            handle_event_creation(message, web_app_data)
        elif web_app_number == 1:
            handle_availability_update(message, web_app_data)
        else:
            print(f"Invalid web_app_number: {web_app_number}")  # Debug log
            bot.send_message(message.chat.id, "Invalid web app type.")
            
    except Exception as e:
        print(f"Error in web app handler: {e}")
        bot.send_message(message.chat.id, "An error occurred. Please try again.")
    finally:
        try:
            # Remove keyboard and send completion message
            bot.send_message(
                message.chat.id,
                "Operation completed.",
                reply_markup=types.ReplyKeyboardRemove()
            )
        except Exception as e:
            print(f"Error in cleanup: {e}")

def handle_event_creation(message, web_app_data):
    """Handle event creation from web app data."""
    try:
        required_fields = ['event_name', 'event_details', 'start', 'end']
        if not all(field in web_app_data for field in required_fields):
            bot.send_message(message.chat.id, "Missing required event data.")
            return
            
        event_name = web_app_data["event_name"]
        event_details = web_app_data["event_details"]
        start_date = web_app_data["start"]
        end_date = web_app_data["end"]
        auto_join = web_app_data.get("auto_join", True)
        event_type = web_app_data.get("event_type", "general")

        if start_date is None or end_date is None:
            bot.send_message(message.chat.id, "Enter in valid date pls")
            return

        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        hours_available = create_hours_available(start_date, end_date)

        text = create_event_text(start_date, end_date)
        event_id = ''.join(random.choices(string.ascii_letters + string.digits, k=16))

        data = {
            "event_name": str(event_name),
            "event_details": str(event_details),
            "event_id": event_id,
            "members": [str(message.chat.id)] if auto_join else [],
            "creator": str(message.chat.id),
            "start_date": start_date,
            "end_date": end_date,
            "hours_available": hours_available,
            "event_type": event_type,
            "text": text + (f"\n <b>{message.from_user.username}</b>" if auto_join else ""),
        }
        
        setEntry("Events", data)
        
        if auto_join:
            ask_availability(message.chat.id, event_id)
        
        markup = types.InlineKeyboardMarkup()
        share_button = types.InlineKeyboardButton(
            text="Share",
            switch_inline_query=f"{event_name}:{event_id}"
        )
        markup.add(share_button)
        
        bot.send_message(
            message.chat.id,
            text + (f"\n <b>{message.from_user.username}</b>" if auto_join else ""),
            reply_markup=markup,
            parse_mode='HTML'
        )
        
    except Exception as e:
        print(f"Error in event creation: {e}")
        bot.send_message(message.chat.id, "Failed to create event. Please try again.")

def handle_availability_update(message, web_app_data):
    """Handle availability update from web app data."""
    try:
        required_fields = ['hours_available', 'event_id']
        if not all(field in web_app_data for field in required_fields):
            bot.send_message(message.chat.id, "Missing required availability data.")
            return
            
        tele_id = message.from_user.id
        tele_username = message.from_user.username
        new_hours_available = web_app_data["hours_available"]["dateTimes"]
        event_id = web_app_data["event_id"]
        
        # Check if username changed
        user_doc = getEntry("Users", "tele_id", str(tele_id))
        if user_doc and user_doc.to_dict().get("tele_user") != tele_username:
            updateUsername(tele_id, tele_username)
        
        # Update availability for specific event
        db_result = getEntry("Events", "event_id", str(event_id))
        
        if not db_result:
            bot.send_message(message.chat.id, "Could not find this event. Please try again.")
            return
        
        updateUserAvailability(tele_username, event_id, new_hours_available)
        bot.send_message(message.chat.id, "Your availability has been saved for this event!")
        
    except Exception as e:
        print(f"Error in availability update: {e}")
        bot.send_message(message.chat.id, "Failed to update availability. Please try again.")

def create_hours_available(start_date, end_date):
    hours_available = []
    for single_date in daterange(start_date, end_date + timedelta(days=1)):
        time_values = []
        for hour in range(24):
            for minute in range(0, 60, 30):
                time_values.append(f"{hour:02d}{minute:02d}")

        day = {str(time): [] for time in time_values}
        day["date"] = single_date
        hours_available.append(day)
    return hours_available

def create_event_text(start_date, end_date):
    return f"""Date range: {start_date.strftime("%-d %b %Y")} - {end_date.strftime("%-d %b %Y")}
Best date: []
Best timing: []

Join this event by clicking the join button below! 

Joining:
---------------
""" 