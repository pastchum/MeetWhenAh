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
from utils.web_app import create_web_app_url

from databases import *
# from scheduling import calculate_optimal_meeting_time  # Import the new scheduling module
# from native_interface import create_native_availability_selector, handle_native_availability_callback

# Import the bot instance and configuration
from src.config.config import bot, logger

# Import all handlers
from src.handlers.command_handlers import *
from src.handlers.event_handlers import *
from src.handlers.availability_handlers import *
from src.handlers.inline_handlers import *

# Import services
from src.services.availability_service import getUserAvailability, updateUserAvailability
from src.services.user_service import getEntry

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

# Webhook endpoint
@app.post(f'/{TOKEN}/')
def process_webhook(update: dict):
	"""Process webhook calls"""
	if update:
		update = telebot.types.Update.de_json(update)
		bot.process_new_updates([update])
	else:
		return

# FastAPI models for API endpoints
class AvailabilityRequest(BaseModel):
	username: str
	event_id: str
	availability_data: list = None

# API endpoints
@app.get('/api/availability/{username}/{event_id}')
async def get_availability(username: str, event_id: str):
	availability = getUserAvailability(username, event_id)
	if availability:
		return {"status": "success", "data": availability}
	else:
		return {"status": "error", "message": "Could not retrieve availability"}

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

# Start the bot if running directly
if __name__ == "__main__":
	logger.info("Starting Telegram bot polling...")
	bot.polling(none_stop=True)
else:
	# When imported as a module, don't start polling
	logger.info("Telegram bot loaded as module")

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

