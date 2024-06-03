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

from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP

from databases import *

load_dotenv()
TOKEN = os.getenv('TOKEN')
WEBHOOK_HOST = os.getenv('WEBHOOK_HOST')
WEBHOOK_PORT = 443
WEBHOOK_URL_BASE = "https://%s:%s" % (WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/%s/" % (TOKEN)



logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)

bot = telebot.TeleBot(TOKEN, parse_mode='HTML') # You can set parse_mode by default. HTML or MARKDOWN
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
		#telebot.types.BotCommand("/event", "Creates a new event")
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
		web_app_info = types.WebAppInfo(url="https://jensenhuangyankai.github.io/meetWhenAh/frontend0/")
		web_app_button = types.KeyboardButton(text="Create Event", web_app=web_app_info)
		markup.add(web_app_button)

		bot.reply_to(message, reply_message, reply_markup=markup)
	
	else:
		bot.reply_to(message, reply_message)
	  


@bot.message_handler(commands=['help'])
def help(message):
	reply_message = """New to <b>meet when ah?</b> <b>DM</b> me <b>/start</b> to create a new event!
	
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
		start_date = web_app_data["start_date"]
		end_date = web_app_data["end_date"]

		if start_date == None or end_date == None:
			bot.send_message(message.chat.id, "Enter in valid date pls")
			return
		start_date = datetime.strptime(start_date, '%d-%m-%Y')
		end_date = datetime.strptime(end_date, '%d-%m-%Y')

		def daterange(start_date, end_date):
			for n in range(int((end_date - start_date).days)):
				yield start_date + timedelta(n)
		hours_available = []

		for single_date in daterange(start_date, end_date):
			day = { str(i): [] for i in range(25) }
			day["0"] = single_date 
			hours_available.append(day)


		text = f"""Date range: {start_date.strftime("%-d %b %Y")} - {end_date.strftime("%-d %b %Y")}

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
		new_hours_available = web_app_data["hours_available"] #data from web app. new.
		event_id = web_app_data["event_id"]
		db_result = getEntry("Events", "event_id", str(event_id))
		hours_already_available = db_result.to_dict()["hours_available"] #data existing in database

		for new_day in new_hours_available:             # old_day = [date][][][][]
			for old_day in hours_already_available:
				if datetime.strptime(new_day["0"], '%d%m%y') == old_day["0"]:
					for i in range(1,24):
						if new_day[str(i)] == 1:
							old_day[str(i)].append(tele_id)

		#write back to db
		updateEntry(db_result, "hours_available", hours_already_available)

	


@bot.inline_handler(lambda query: len(query.query) > 0)
def query_text(inline_query):
	try:
		event_name = inline_query.query.split(":")[0]
		event_id = inline_query.query.split(":")[1]
		result = getEntry("Events", "event_id", event_id)
		text = result.to_dict()["text"]
		
		#updateEntry(result, "inline_message_id", str(inline_query.id))

		r = types.InlineQueryResultArticle(
			id='1', title=inline_query.query,
			input_message_content=types.InputTextMessageContent(text),
			reply_markup=types.InlineKeyboardMarkup().add(
				types.InlineKeyboardButton('Join event', callback_data=result.to_dict()["event_id"])
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
	message_id = call.inline_message_id
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
		
	#elif db_result2.to_dict()["initialised"] == False:
	#	return
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
								types.InlineKeyboardButton('Join event', callback_data=event_id)))

def ask_availability(tele_id, event_id):
	ic("here")
	text = "Click the button below to set your availability!"
	db_result = getEntry("Events", "event_id", str(event_id))
	start_date = db_result.to_dict()["start_date"]
	end_date = db_result.to_dict()["end_date"]
	event_name = db_result.to_dict()["event_name"]

	data = {"event_id": event_id,
		 	"startDate" : start_date.strftime('%Y-%m-%d'),
			"endDate" : end_date.strftime('%Y-%m-%d'),
			"event_name": event_name
		}
	

	markup = types.ReplyKeyboardMarkup(row_width=1)
	url = create_web_app_url("https://jensenhuangyankai.github.io/meetWhenAh/frontend1/", data=data)
	print(url)
	web_app_info = types.WebAppInfo(url=url)
	web_app_button = types.KeyboardButton(text="Set availability", web_app=web_app_info)
	markup.add(web_app_button)

	bot.send_message(tele_id, text, reply_markup=markup)







############################# WEBHOOK STUFF ###############################################
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

bot.remove_webhook()
time.sleep(0.1)
# Set webhook
bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH)
				#certificate=open(WEBHOOK_SSL_CERT, 'r'))



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

