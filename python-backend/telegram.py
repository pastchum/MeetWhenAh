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
		telebot.types.BotCommand("/sleep", "Set your sleep hours")
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

Use <b>/sleep</b> to set your sleep hours to improve scheduling.
	
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
			"event_name" : str(event_name),
			"event_details" : str(event_details),
			"event_id" : ''.join(random.choices(string.ascii_letters + string.digits, k=16)),
			"members" : [],
			"creator" : str(message.chat.id),
			"start_date" : start_date,
			"end_date" : end_date,
			"hours_available": hours_available,
			"event_type": event_type,  # Store the event type
			"text" : text,
			
		}
		bot.send_message(message.chat.id, "You can continue to additional settings by clicking the button below, or click done.")
		setEntry("Events", data)
		markup = types.InlineKeyboardMarkup()
		share_button = types.InlineKeyboardButton(text="Share", switch_inline_query=data["event_name"] + ":" + data["event_id"])
		markup.add(share_button)
		bot.send_message(message.chat.id, text, reply_markup=markup)


	elif web_app_number == 1:
		tele_id = message.from_user.id
		new_hours_available = web_app_data["hours_available"]["dateTimes"] #data from web app. new.
		event_id = web_app_data["event_id"]
		db_result = getEntry("Events", "event_id", str(event_id))
		
		if not db_result:
			bot.send_message(message.chat.id, "Could not find this event. Please try again.")
			return
			
		event_data = db_result.to_dict()
		hours_already_available = event_data["hours_available"] #data existing in database
		event_type = event_data.get("event_type", "general")  # Get event type

		# Save the user's availability for this specific event
		for new_day in new_hours_available:
			for old_day in hours_already_available:
				if datetime.strptime(new_day['date'], '%d/%m/%Y').date() == old_day["date"].date():
					old_day[new_day['time']].append(tele_id)

		# Also save this availability pattern to user's profile for this event type
		user_doc = getEntry("Users", "tele_id", str(tele_id))
		
		if user_doc:
			user_data = user_doc.to_dict()
			
			# Initialize availability_patterns if it doesn't exist
			if "availability_patterns" not in user_data:
				user_data["availability_patterns"] = {}
				
			# Initialize this event type if it doesn't exist
			if event_type not in user_data["availability_patterns"]:
				user_data["availability_patterns"][event_type] = {}
				
			# Save patterns by day of week
			for new_day in new_hours_available:
				day_date = datetime.strptime(new_day['date'], '%d/%m/%Y')
				day_of_week = day_date.strftime('%A')  # Monday, Tuesday, etc.
				
				# Save time slot for this day of week
				if day_of_week not in user_data["availability_patterns"][event_type]:
					user_data["availability_patterns"][event_type][day_of_week] = []
					
				user_data["availability_patterns"][event_type][day_of_week].append(new_day['time'])
				
			# Update the user document
			updateEntry(user_doc, "availability_patterns", user_data["availability_patterns"])
			
			bot.send_message(
				message.chat.id, 
				f"Your availability for {event_type} events has been saved to your profile and will be suggested for future events!"
			)

		# Update the event's availability
		updateEntry(db_result, "hours_available", hours_already_available)




@bot.inline_handler(lambda query: len(query.query) > 0)
def query_text(inline_query):
	try:
		event_name = inline_query.query.split(":")[0]
		event_id = inline_query.query.split(":")[1]
		result = getEntry("Events", "event_id", event_id)
		text = result.to_dict()["text"]
		
	
		r = types.InlineQueryResultArticle(
			id='1', title=inline_query.query,
			input_message_content=types.InputTextMessageContent(text),
			reply_markup=types.InlineKeyboardMarkup().add(
				types.InlineKeyboardButton('Join event', callback_data=result.to_dict()["event_id"]),
				types.InlineKeyboardButton('Calculate Best Timing', callback_data=str("Calculate " + result.to_dict()["event_id"]))
			)
		)
		bot.answer_inline_query(inline_query.id, [r])
	except Exception as e:
		print(e)


def create_web_app_url(base_url, data):
    #base_url = 'https://your-web-app.com/'
    # Assuming 'data' is a dictionary, convert it to a query string

	query_string = urllib.parse.urlencode(data)
	ic(query_string)
	ic(data)
	return f"{base_url}?{query_string}"


@bot.callback_query_handler(func=lambda call: call)
def handle_join_event(call):
	new_text = ""
	message_id = call.inline_message_id
	if "Calculate" in str(call.data): 
		event_id = str(call.data).split()[1]
		
		db_result = getEntry("Events", "event_id", event_id)
		hours_available = db_result.to_dict()["hours_available"]
		original_text = db_result.to_dict()["text"]
		
		# Get sleep preferences for event members
		event_sleep_prefs = getEventSleepPreferences(event_id)
		
		# Calculate average sleep hours if preferences exist
		if event_sleep_prefs:
			total_start = 0
			total_end = 0
			total_users = len(event_sleep_prefs)
			
			for user_id, prefs in event_sleep_prefs.items():
				total_start += int(prefs["start"])
				total_end += int(prefs["end"])
			
			avg_start = round(total_start / total_users)
			avg_end = round(total_end / total_users)
			
			# Format to proper string format
			avg_start_str = f"{avg_start:04d}"
			avg_end_str = f"{avg_end:04d}"
			
			sleep_hours = {
				"start": avg_start_str,
				"end": avg_end_str
			}
			
			# Use the new scheduling algorithm with sleep preferences
			best_date = calculate_optimal_meeting_time(hours_available, sleep_hours)
		else:
			# Use default sleep hours if no preferences
			best_date = calculate_optimal_meeting_time(hours_available)
		
		ic(best_date)
		date_pattern = r'Best date:\s*\[\]'
		timing_pattern = r'Best timing:\s*\[\]'

		# Format the date for display
		if best_date['final_date'] is not None:
			formatted_date = best_date['final_date'].date()
			# Format the time in a readable format
			start_time = best_date['final_start_timing']
			end_time = best_date['final_end_timing']
			
			# Convert from HHMM to more readable format
			start_formatted = f"{start_time[:2]}:{start_time[2:]}"
			end_formatted = f"{end_time[:2]}:{end_time[2:]}"
			
			best_timing_str = f"{start_formatted} - {end_formatted}"
			
			# Format participants list
			participants_str = ""
			if best_date['participants']:
				participants_str = ", ".join([f"@{bot.get_chat(int(p)).username}" for p in best_date['participants'] if bot.get_chat(int(p)).username])
				
			new_text = re.sub(date_pattern, f"Best date: {formatted_date}", original_text)
			new_text = re.sub(timing_pattern, f"Best timing: [{best_timing_str}]", new_text)
			
			# Add participants info if available
			if participants_str:
				new_text += f"\n\nAvailable participants: {participants_str}"
		else:
			new_text = re.sub(date_pattern, "Best date: No suitable date found", original_text)
			new_text = re.sub(timing_pattern, "Best timing: No suitable time found", new_text)
			
		updateEntry(db_result, "text", new_text)

	else:
		
		db_result = getEntry("Events", "event_id", str(call.data))
		members = db_result.to_dict()["members"]
		if str(call.from_user.id) in members:
			return
		
		event_id = db_result.to_dict()["event_id"]
		original_text = db_result.to_dict()["text"]
		
		db_result2 = getEntry("Users", "tele_id", str(call.from_user.id))
		if db_result2 == None:
			new_text = original_text + f"\n <b>@{call.from_user.username}, please do /start in a direct message with me at @meetwhenah_bot. Click the join button again when you are done!</b>"
			updateEntry(db_result, "text", new_text)

			setEntry("Users", {"tele_id" : str(call.from_user.id),
						"tele_user" : str(call.from_user.username),
						"initialised" : False,
						"callout_cleared" : False})
			

		elif db_result2.to_dict()["initialised"] == True and db_result2.to_dict()["callout_cleared"] == False:
			old_string = f"\n <b>@{call.from_user.username}, please do /start in a private message with me at @meetwhenah_bot. Click the join button again when you are done!</b>"
			new_text = original_text.replace(old_string, "")

			members.append(str(call.from_user.id))
			updateEntry(db_result, "members", members)
			new_text = new_text + f"\n <b>{call.from_user.username}</b>"
			updateEntry(db_result, "text", new_text)

		else:
			#this is the part where the user is initalised and added into db
			members.append(str(call.from_user.id))
			updateEntry(db_result, "members", members)
			new_text = original_text + f"\n <b>{call.from_user.username}</b>"
			updateEntry(db_result, "text", new_text)
			ask_availability(call.from_user.id, event_id)
			ic("Asking Availability...")


	bot.edit_message_text(text = f"{new_text}",
							inline_message_id=message_id,
							reply_markup=types.InlineKeyboardMarkup().add(
								types.InlineKeyboardButton('Join event', callback_data=event_id),
								types.InlineKeyboardButton('Calculate Best Timing', callback_data=str("Calculate " + event_id))))

def ask_availability(tele_id, event_id):
	ic("here")
	text = "Click the button below to set your availability!"
	db_result = getEntry("Events", "event_id", str(event_id))
	start_date = db_result.to_dict()["start_date"]
	end_date = db_result.to_dict()["end_date"]
	event_name = db_result.to_dict()["event_name"]
	event_type = db_result.to_dict().get("event_type", "general")  # Get event type

	# Get user's saved availability pattern for this event type
	user_doc = getEntry("Users", "tele_id", str(tele_id))
	saved_pattern = None
	
	if user_doc and "availability_patterns" in user_doc.to_dict():
		patterns = user_doc.to_dict()["availability_patterns"]
		if event_type in patterns:
			saved_pattern = patterns[event_type]
			text = "Click the button below to set your availability! We've pre-filled it with your saved preferences for this type of event."

	data = {
		"event_id": event_id,
		"start" : start_date.strftime('%Y-%m-%d'),
		"end" : end_date.strftime('%Y-%m-%d'),
		"event_name": event_name,
		"event_type": event_type
	}
	
	# Add saved pattern if available
	if saved_pattern:
		data["saved_pattern"] = json.dumps(saved_pattern)
	

	markup = types.ReplyKeyboardMarkup(row_width=1)
	url = create_web_app_url("https://meet-when-ah.vercel.app/dragselector/", data=data)
	print(url)
	web_app_info = types.WebAppInfo(url=url)
	web_app_button = types.KeyboardButton(text="Set availability", web_app=web_app_info)
	markup.add(web_app_button)

	bot.send_message(tele_id, text, reply_markup=markup)


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
bot.polling(none_stop=True)
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

