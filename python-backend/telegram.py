from dotenv import load_dotenv
import telebot
from telebot import types
from telebot.util import quick_markup
import logging
import os
import fastapi
from fastapi import Request
from pydantic import BaseModel
from typing import Union
import uvicorn
import time
from icecream import ic
from datetime import datetime, date, timedelta
import random
import string
import urllib.parse
import re
import json

from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP

from databases import *
from scheduling import calculate_optimal_meeting_time  # Import the new scheduling module
from native_interface import create_native_availability_selector, handle_native_availability_callback

load_dotenv()
TOKEN = os.getenv('TOKEN')
#WEBHOOK_HOST = os.getenv('WEBHOOK_HOST')
#AWS_ENDPOINT = os.getenv('AWS_ENDPOINT')
#WEBHOOK_PORT = 443
#WEBHOOK_URL_BASE = "https://%s:%s" % (WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/%s/" % (TOKEN)



logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)

bot = telebot.TeleBot(TOKEN, parse_mode='HTML', threaded=False) # You can set parse_mode by default. HTML or MARKDOWN
app = fastapi.FastAPI(docs=None, redoc_url=None)
app.type = "00"

# Empty webserver index, return nothing, just http 200
@app.get('/')
def index():
	return ''



#"""######################################COMMANDS"""
bot.set_my_commands(
	commands=[
		telebot.types.BotCommand("/start", "Starts the bot!"),
		telebot.types.BotCommand("/help", "Help"),
		telebot.types.BotCommand("/sleep", "Set your sleep hours"),
		telebot.types.BotCommand("/myavailability", "Check your availability for an event"),
		telebot.types.BotCommand("/updateavailability", "Update your availability for an event")
	],
	# scope=telebot.types.BotCommandScopeChat(12345678)  # use for personal command for users
	# scope=telebot.types.BotCommandScopeAllPrivateChats()  # use for all private chats
)

@bot.message_handler(commands=['start'])
def send_welcome(message):
	reply_message = """<b>meet when ah? –</b> Say hello to efficient planning and wave goodbye to "so when r we meeting ah?". 
This bot is for the trip that <b>will</b> make it out of the groupchat. 

Click <b>Create Event</b> to get started <b>now</b>!

Need help? Type /help for more info on commands!
	""" # Create events in private messages using /event, and send your invites to the group!

	if message.chat.type == 'private':
		db_result = getEntry("Users", "tele_id", str(message.from_user.id))
		if db_result == None:
			setEntry("Users", {"tele_id" : str(message.from_user.id),
							"tele_user" : str(message.from_user.username),
							"initialised" : True,
							"callout_cleared" : True})
		else:
			if db_result.to_dict()["initialised"] == False:
				updateEntry(db_result, "initialised", True)
				updateEntry(db_result, "callout_cleared", True)
			if db_result.to_dict()["callout_cleared"] == True: #this is in case an initialised user tries to /start again
				pass
			#else:
			#	updateEntry(db_result, "callout_cleared", False) 

		markup = types.ReplyKeyboardMarkup(row_width=1)
		web_app_info = types.WebAppInfo(url="https://meet-when-ah.vercel.app/datepicker")
		web_app_button = types.KeyboardButton(text="Create Event", web_app=web_app_info)
		markup.add(web_app_button)

		bot.reply_to(message, reply_message, reply_markup=markup)
	
	else:
		bot.reply_to(message, reply_message)
	  


@bot.message_handler(commands=['help'])
def help(message):
	reply_message = """New to <b>meet when ah?</b> <b>DM</b> me <b>/start</b> to create a new event!

Available commands:
- <b>/start</b> - Create a new event
- <b>/sleep</b> - Set your sleep hours to improve scheduling
- <b>/myavailability</b> - Check your availability for an event
- <b>/updateavailability</b> - Update your availability for an existing event
	
	"""
	bot.reply_to(message, reply_message)
	
@bot.message_handler(content_types=['web_app_data'])
def handle_webapp(message):
	bot.send_message(message.chat.id, "Event Saved!", reply_markup=types.ReplyKeyboardRemove())
	web_app_data = json.loads(message.web_app_data.data)
	ic(web_app_data)
	web_app_number = web_app_data["web_app_number"]
	if web_app_number == 0:
		event_name = web_app_data["event_name"]
		event_details = web_app_data["event_details"]
		start_date = web_app_data["start"]
		end_date = web_app_data["end"]
		auto_join = web_app_data.get("auto_join", True)  # Default to True if not specified
		
		# Add optional event type field (if provided)
		event_type = web_app_data.get("event_type", "general")

		if start_date is None or end_date is None:
			bot.send_message(message.chat.id, "Enter in valid date pls")
			return
		start_date = datetime.strptime(start_date, '%Y-%m-%d')
		end_date = datetime.strptime(end_date, '%Y-%m-%d')

		def daterange(start_date, end_date):
			for n in range(int((end_date - start_date).days)):
				yield start_date + timedelta(n)
		hours_available = []

		for single_date in daterange(start_date, end_date + timedelta(days=1)):
			time_values = []
			for hour in range(24):
				for minute in range(0, 60, 30):
					time_values.append(f"{hour:02}{minute:02}")

			day = { str(time): [] for time in time_values }
			day["date"] = single_date
			hours_available.append(day)

		text = f"""Date range: {start_date.strftime("%-d %b %Y")} - {end_date.strftime("%-d %b %Y")}
Best date: []
Best timing: []

Join this event by clicking the join button below! 

Joining:
---------------
"""
		data = {
			"event_name": str(event_name),
			"event_details": str(event_details),
			"event_id": ''.join(random.choices(string.ascii_letters + string.digits, k=16)),
			"members": [str(message.chat.id)] if auto_join else [],  # Add creator to members if auto_join is True
			"creator": str(message.chat.id),
			"start_date": start_date,
			"end_date": end_date,
			"hours_available": hours_available,
			"event_type": event_type,
			"text": text + (f"\n <b>{message.from_user.username}</b>" if auto_join else ""),  # Add creator to text if auto_join is True
		}
		
		setEntry("Events", data)
		
		# If auto_join is True, ask for availability
		if auto_join:
			ask_availability(message.chat.id, data["event_id"])
		
		# Create share button
		markup = types.InlineKeyboardMarkup()
		share_button = types.InlineKeyboardButton(text="Share", switch_inline_query=data["event_name"] + ":" + data["event_id"])
		markup.add(share_button)
		bot.send_message(message.chat.id, text + (f"\n <b>{message.from_user.username}</b>" if auto_join else ""), reply_markup=markup, parse_mode='HTML')


	elif web_app_number == 1:
		tele_id = message.from_user.id
		tele_username = message.from_user.username
		new_hours_available = web_app_data["hours_available"]["dateTimes"] #data from web app. new.
		event_id = web_app_data["event_id"]
		
		# Check if username changed
		user_doc = getEntry("Users", "tele_id", str(tele_id))
		if user_doc and user_doc.to_dict().get("tele_user") != tele_username:
			# Update username
			updateUsername(tele_id, tele_username)
		
		# Update availability for specific event
		db_result = getEntry("Events", "event_id", str(event_id))
		
		if not db_result:
			bot.send_message(message.chat.id, "Could not find this event. Please try again.")
			return
			
		# Use the new function to update availability
		updateUserAvailability(tele_username, event_id, new_hours_available)
		
		bot.send_message(
			message.chat.id, 
			f"Your availability has been saved for this event!"
		)




@bot.inline_handler(lambda query: len(query.query) > 0)
def query_text(inline_query):
    try:
        event_name = inline_query.query.split(":")[0]
        event_id = inline_query.query.split(":")[1]
        result = getEntry("Events", "event_id", event_id)
        
        if not result:
            bot.answer_inline_query(inline_query.id, [])
            return
            
        event_data = result.to_dict()
        text = event_data["text"]
        
        # Create a more descriptive title
        title = f"📅 {event_name}"
        
        # Create the inline result with HTML parse mode
        r = types.InlineQueryResultArticle(
            id='1',
            title=title,
            description="Click to join this event!",
            input_message_content=types.InputTextMessageContent(
                message_text=text,
                parse_mode='HTML'
            ),
            reply_markup=types.InlineKeyboardMarkup().row(
                types.InlineKeyboardButton('Join event', callback_data=f"Join_{event_id}"),
                types.InlineKeyboardButton('Update Availability', callback_data=f"Update_{event_id}")
            ).add(
                types.InlineKeyboardButton('Calculate Best Timing', callback_data=f"Calculate_{event_id}")
            )
        )
        bot.answer_inline_query(inline_query.id, [r], cache_time=1)
    except Exception as e:
        ic(f"Error in inline query: {e}")
        bot.answer_inline_query(inline_query.id, [])

@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    try:
        if call.data.startswith("Join_"):
            event_id = call.data.split("_")[1]
            handle_join_event(call, event_id)
        elif call.data.startswith("Update_"):
            event_id = call.data.split("_")[1]
            ask_availability(call.from_user.id, event_id)
            bot.answer_callback_query(call.id, "Opening availability selector...")
        elif call.data.startswith("Calculate_"):
            event_id = call.data.split("_")[1]
            handle_calculate(call, event_id)
    except Exception as e:
        ic(f"Error in callback query: {e}")
        bot.answer_callback_query(call.id, "An error occurred. Please try again.")

def handle_join_event(call, event_id):
    db_result = getEntry("Events", "event_id", event_id)
    if not db_result:
        bot.answer_callback_query(call.id, "Event not found!")
        return
        
    event_data = db_result.to_dict()
    members = event_data.get("members", [])
    
    if str(call.from_user.id) in members:
        bot.answer_callback_query(call.id, "You've already joined this event!")
        return
    
    # Check if user is initialized
    db_result2 = getEntry("Users", "tele_id", str(call.from_user.id))
    if not db_result2:
        new_text = event_data["text"] + f"\n <b>@{call.from_user.username}, please do /start in a direct message with me at @meetwhenah_bot. Click the join button again when you are done!</b>"
        updateEntry(db_result, "text", new_text)
        setEntry("Users", {
            "tele_id": str(call.from_user.id),
            "tele_user": str(call.from_user.username),
            "initialised": False,
            "callout_cleared": False
        })
    else:
        # Add user to members
        members.append(str(call.from_user.id))
        new_text = event_data["text"] + f"\n <b>{call.from_user.username}</b>"
        updateEntry(db_result, "text", new_text)
        updateEntry(db_result, "members", members)
        ask_availability(call.from_user.id, event_id)
        bot.answer_callback_query(call.id, "Welcome to the event! Setting up availability selector...")
    
    # Update the message with new text and buttons
    bot.edit_message_text(
        text=new_text,
        inline_message_id=call.inline_message_id,
        parse_mode='HTML',
        reply_markup=types.InlineKeyboardMarkup().row(
            types.InlineKeyboardButton('Join event', callback_data=f"Join_{event_id}"),
            types.InlineKeyboardButton('Update Availability', callback_data=f"Update_{event_id}")
        ).add(
            types.InlineKeyboardButton('Calculate Best Timing', callback_data=f"Calculate_{event_id}")
        )
    )

def handle_calculate(call, event_id):
    db_result = getEntry("Events", "event_id", event_id)
    if not db_result:
        bot.answer_callback_query(call.id, "Event not found!")
        return
        
    event_data = db_result.to_dict()
    hours_available = event_data["hours_available"]
    original_text = event_data["text"]
    
    # Get sleep preferences for event members
    event_sleep_prefs = getEventSleepPreferences(event_id)
    
    # Calculate optimal meeting time
    if event_sleep_prefs:
        total_start = sum(int(prefs["start"]) for prefs in event_sleep_prefs.values())
        total_end = sum(int(prefs["end"]) for prefs in event_sleep_prefs.values())
        total_users = len(event_sleep_prefs)
        
        avg_start = round(total_start / total_users)
        avg_end = round(total_end / total_users)
        
        sleep_hours = {
            "start": f"{avg_start:04d}",
            "end": f"{avg_end:04d}"
        }
        best_date = calculate_optimal_meeting_time(hours_available, sleep_hours)
    else:
        best_date = calculate_optimal_meeting_time(hours_available)
    
    # Update text with results
    if best_date['final_date'] is not None:
        formatted_date = best_date['final_date'].date()
        start_time = f"{best_date['final_start_timing'][:2]}:{best_date['final_start_timing'][2:]}"
        end_time = f"{best_date['final_end_timing'][:2]}:{best_date['final_end_timing'][2:]}"
        best_timing_str = f"{start_time} - {end_time}"
        
        participants_str = ""
        if best_date['participants']:
            participants_str = ", ".join([f"@{bot.get_chat(int(p)).username}" for p in best_date['participants'] if bot.get_chat(int(p)).username])
        
        new_text = re.sub(r'Best date:\s*\[\]', f"Best date: {formatted_date}", original_text)
        new_text = re.sub(r'Best timing:\s*\[\]', f"Best timing: [{best_timing_str}]", new_text)
        
        if participants_str:
            new_text += f"\n\nAvailable participants: {participants_str}"
    else:
        new_text = re.sub(r'Best date:\s*\[\]', "Best date: No suitable date found", original_text)
        new_text = re.sub(r'Best timing:\s*\[\]', "Best timing: No suitable time found", new_text)
    
    updateEntry(db_result, "text", new_text)
    
    # Update the message
    bot.edit_message_text(
        text=new_text,
        inline_message_id=call.inline_message_id,
        parse_mode='HTML',
        reply_markup=types.InlineKeyboardMarkup().row(
            types.InlineKeyboardButton('Join event', callback_data=f"Join_{event_id}"),
            types.InlineKeyboardButton('Update Availability', callback_data=f"Update_{event_id}")
        ).add(
            types.InlineKeyboardButton('Calculate Best Timing', callback_data=f"Calculate_{event_id}")
        )
    )

def ask_availability(tele_id, event_id):
	ic("here")
	db_result = getEntry("Events", "event_id", str(event_id))
	if not db_result:
		bot.send_message(tele_id, "Could not find this event. Please try again.")
		return
		
	event_data = db_result.to_dict()
	start_date = event_data["start_date"]
	end_date = event_data["end_date"]
	event_name = event_data["event_name"]
	event_type = event_data.get("event_type", "general")

	# Get user's saved availability pattern for this event type
	user_doc = getEntry("Users", "tele_id", str(tele_id))
	saved_pattern = None
	
	if user_doc and "availability_patterns" in user_doc.to_dict():
		patterns = user_doc.to_dict()["availability_patterns"]
		if event_type in patterns:
			saved_pattern = patterns[event_type]
			text = "We've pre-filled your availability with your saved preferences for this type of event."
		else:
			text = "Click the button below to set your availability!"
	else:
		text = "Click the button below to set your availability!"

	# Create data for web app
	data = {
		"event_id": event_id,
		"start": start_date.strftime('%Y-%m-%d'),
		"end": end_date.strftime('%Y-%m-%d'),
		"event_name": event_name,
		"event_type": event_type
	}
	
	# Add saved pattern if available
	if saved_pattern:
		data["saved_pattern"] = json.dumps(saved_pattern)
	
	# Create inline keyboard with both options
	markup = types.InlineKeyboardMarkup(row_width=2)
	
	# Web app button
	web_app_info = types.WebAppInfo(url=create_web_app_url("https://meet-when-ah.vercel.app/dragselector/", data))
	web_app_button = types.InlineKeyboardButton("Web Interface", web_app=web_app_info)
	
	# Native interface button
	native_button = types.InlineKeyboardButton("Native Interface", callback_data=f"Native_{event_id}")
	
	markup.add(web_app_button, native_button)
	
	bot.send_message(tele_id, text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("Native_"))
def handle_native_interface(call):
	event_id = call.data.split("_")[1]
	db_result = getEntry("Events", "event_id", str(event_id))
	
	if not db_result:
		bot.answer_callback_query(call.id, "Could not find this event!")
		return
		
	event_data = db_result.to_dict()
	
	# Create native interface
	text, markup = create_native_availability_selector(bot, call.message, event_id, event_data)
	
	# Edit the message to show the native interface
	bot.edit_message_text(
		text,
		call.message.chat.id,
		call.message.message_id,
		reply_markup=markup
	)
	
	# Answer the callback query
	bot.answer_callback_query(call.id)

# Update the callback query handler to handle native interface callbacks
@bot.callback_query_handler(func=lambda call: call.data.startswith(("Slot_", "Save_", "Cancel_")))
def handle_native_callbacks(call):
	handle_native_availability_callback(bot, call)

############################# WEBHOOK STUFF ###############################################
#bot.remove_webhook()
@app.post(f'/{TOKEN}/')
def process_webhook(update: dict):
	"""
	Process webhook calls
	"""
	if update:
		update = telebot.types.Update.de_json(update)
		bot.process_new_updates([update])
	else:
		return

#Set webhook
#bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH)
#				certificate=open(WEBHOOK_SSL_CERT, 'r'))

########################### LAMBDA STUFF #################################################
#bot.remove_webhook()
# time.sleep(0.1)

# webhook_info = bot.get_webhook_info()
# ic(webhook_info)
# if not webhook_info.url:
# 	bot.set_webhook(url=AWS_ENDPOINT)

# def lambda_handler(event, context):
# 	update = types.Update.de_json(json.loads(event['body']))
# 	bot.process_new_updates([update])
# 	return {
# 		'statusCode': 200,
# 		'body': json.dumps('Hello from Lambda!')
# 	}

# If the file is run directly, start polling
if __name__ == "__main__":
    print("Starting Telegram bot polling...")
    bot.polling(none_stop=True)
else:
    # When imported as a module, don't start polling
    # Remove this line
    # bot.polling(none_stop=True)
    pass

"""
@bot.message_handler(commands=['event'])
def new_event(message):
	if message.chat.type == 'private':
		
		global start_date
		global end_date
		start_date = ""
		end_date = ""
		markup = types.ForceReply(selective=False)
		msg = bot.send_message(message.chat.id, "Please send me the name of your event:", reply_markup=markup)
		bot.register_next_step_handler(msg, share)
	else:
		bot.reply_to(message, "This command only works when you <i>private message</i> me at @meetwhenah_bot!")
"""

"""
start_date = ""
end_date = ""

@bot.message_handler(commands=['event'])
def new_event(message):
	global start_date
	global end_date
	start_date = ""
	end_date = ""
	markup = types.ForceReply(selective=False)
	msg = bot.send_message(message.chat.id, "Please send me the name of your event:", reply_markup=markup)
	bot.register_next_step_handler(msg, event_description)

def event_description(message):
	text = "Please send me the description of your event: (if any)"
	markup = quick_markup({
		'None' : {'callback_data': 'yes'},
	},row_width=1)

	msg = bot.send_message(message.chat.id, text, reply_markup=markup)
	bot.register_next_step_handler(msg, set_start_date)



def set_start_date(message):
	bot.send_message(message.chat.id, "Now, please select the <b>Start Date</b> of your event.")
	calendar, step = DetailedTelegramCalendar().build()
	bot.send_message(message.chat.id,
					 f"Select start date",
					 reply_markup=calendar)

def set_end_date(message):
	bot.send_message(message.chat.id, "Now, please select the <b>End Date</b> of your event.")
	calendar, step = DetailedTelegramCalendar().build()
	bot.send_message(message.chat.id,
					 f"Select end date",
					 reply_markup=calendar)

@bot.callback_query_handler(func=DetailedTelegramCalendar.func())
def cal(c):
	result, key, step = DetailedTelegramCalendar().process(c.data)
	if not result and key:
		bot.edit_message_text(f"Select {LSTEP[step]}",
							  c.message.chat.id,
							  c.message.message_id,
							  reply_markup=key)
	elif result:
		bot.edit_message_text(f"Saved. Date picked was {result}",
							  c.message.chat.id,
							  c.message.message_id)
		
		global start_date
		global end_date
		if start_date == "":
			start_date = result
			set_end_date(c.message)
		else:
			end_date = result
			share(c.message)
			#ic(start_date)
			#ic(end_date)
"""

# New command to set sleep preferences
@bot.message_handler(commands=['sleep'])
def sleep_command(message):
	# This command only works in private chats
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
		
	except ValueError as e:
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
		
	except ValueError as e:
		bot.send_message(
			message.chat.id,
			"Invalid time format. Please use HHMM format (e.g., 0700 for 7:00 AM). Try /sleep again."
		)

# Create a new command to check your own availability for an event
@bot.message_handler(commands=['myavailability'])
def check_availability(message):
	if message.chat.type != 'private':
		bot.reply_to(message, "This command only works in private chat. Please message me directly.")
		return
		
	markup = types.ForceReply(selective=False)
	bot.send_message(
		message.chat.id, 
		"Please enter the event ID to check your availability:",
		reply_markup=markup
	)
	bot.register_next_step_handler(message, process_check_availability)

def process_check_availability(message):
	event_id = message.text.strip()
	tele_username = message.from_user.username
	
	# Get availability for this user and event
	availability = getUserAvailability(tele_username, event_id)
	
	if not availability:
		bot.send_message(
			message.chat.id,
			"Could not find your availability for this event. Have you set your availability yet?"
		)
		return
	
	# Format availability for display
	availability_by_day = {}
	for slot in availability:
		date = slot["date"]
		time = slot["time"]
		
		if date not in availability_by_day:
			availability_by_day[date] = []
			
		availability_by_day[date].append(time)
	
	# Generate text summary
	response = "Your availability for this event:\n\n"
	
	for date, times in availability_by_day.items():
		try:
			# Format the date nicely
			date_obj = datetime.strptime(date, "%Y-%m-%d")
			formatted_date = date_obj.strftime("%A, %B %d, %Y")
			
			# Sort times
			times.sort()
			
			# Find contiguous blocks
			blocks = []
			current_block = [times[0]]
			
			for i in range(1, len(times)):
				# Check if times are consecutive
				last_hour = int(current_block[-1][:2])
				last_minute = int(current_block[-1][2:])
				last_total_minutes = last_hour * 60 + last_minute
				
				curr_hour = int(times[i][:2])
				curr_minute = int(times[i][2:])
				curr_total_minutes = curr_hour * 60 + curr_minute
				
				if curr_total_minutes - last_total_minutes == 30:
					# Consecutive time slot
					current_block.append(times[i])
				else:
					# Start a new block
					blocks.append(current_block)
					current_block = [times[i]]
			
			# Add the last block
			blocks.append(current_block)
			
			# Format the blocks
			time_ranges = []
			for block in blocks:
				start_time = block[0]
				end_time = block[-1]
				
				# Format for display (HHMM -> HH:MM)
				start_formatted = f"{start_time[:2]}:{start_time[2:]}"
				
				# Add 30 minutes to the end time
				end_hour = int(end_time[:2])
				end_minute = int(end_time[2:]) + 30
				if end_minute >= 60:
					end_hour += 1
					end_minute -= 60
				end_formatted = f"{end_hour:02d}:{end_minute:02d}"
				
				time_ranges.append(f"{start_formatted} - {end_formatted}")
			
			response += f"{formatted_date}:\n"
			for time_range in time_ranges:
				response += f"• {time_range}\n"
			response += "\n"
			
		except Exception as e:
			ic(f"Error formatting availability: {e}")
			response += f"{date}: {', '.join(times)}\n\n"
	
	bot.send_message(message.chat.id, response)

# Add a command to allow users to update specific event availability
@bot.message_handler(commands=['updateavailability'])
def update_availability(message):
	if message.chat.type != 'private':
		bot.reply_to(message, "This command only works in private chat. Please message me directly.")
		return
		
	# Get all events where the user is a member
	user_id = str(message.from_user.id)
	events_ref = db.collection("Events")
	user_events = []
	
	# Query events where the user is a member
	for doc in events_ref.stream():
		event_data = doc.to_dict()
		if user_id in event_data.get("members", []):
			user_events.append({
				"event_id": event_data["event_id"],
				"event_name": event_data["event_name"],
				"start_date": event_data["start_date"].strftime("%Y-%m-%d"),
				"end_date": event_data["end_date"].strftime("%Y-%m-%d")
			})
	
	if not user_events:
		bot.reply_to(message, "You haven't joined any events yet!")
		return
	
	# Create inline keyboard with event buttons
	markup = types.InlineKeyboardMarkup(row_width=1)
	for event in user_events:
		button_text = f"{event['event_name']} ({event['start_date']} to {event['end_date']})"
		callback_data = f"Update {event['event_id']}"
		markup.add(types.InlineKeyboardButton(button_text, callback_data=callback_data))
	
	bot.reply_to(
		message,
		"Select an event to update your availability:",
		reply_markup=markup
	)

# Add FastAPI model for API requests
class AvailabilityRequest(BaseModel):
    username: str
    event_id: str
    availability_data: list = None
    
# API endpoint to get a user's availability
@app.get('/api/availability/{username}/{event_id}')
async def get_availability(username: str, event_id: str):
    availability = getUserAvailability(username, event_id)
    if availability:
        return {"status": "success", "data": availability}
    else:
        return {"status": "error", "message": "Could not retrieve availability"}

# API endpoint to update a user's availability
@app.post('/api/availability')
async def update_availability(request: AvailabilityRequest):
    success = updateUserAvailability(
        request.username, 
        request.event_id, 
        request.availability_data
    )
    
    if success:
        return {"status": "success", "message": "Availability updated successfully"}
    else:
        return {"status": "error", "message": "Failed to update availability"}
        
# API endpoint to get event details
@app.get('/api/event/{event_id}')
async def get_event(event_id: str):
    event_doc = getEntry("Events", "event_id", str(event_id))
    
    if not event_doc:
        return {"status": "error", "message": "Event not found"}
        
    event_data = event_doc.to_dict()
    
    # Format dates for JSON serialization
    if "start_date" in event_data:
        event_data["start_date"] = event_data["start_date"].strftime("%Y-%m-%d")
    if "end_date" in event_data:
        event_data["end_date"] = event_data["end_date"].strftime("%Y-%m-%d")
        
    # Format hours_available dates
    for day in event_data.get("hours_available", []):
        if "date" in day and hasattr(day["date"], "strftime"):
            day["date"] = day["date"].strftime("%Y-%m-%d")
    
    return {"status": "success", "data": event_data}

