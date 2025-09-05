import os
import json
from datetime import datetime, timedelta
import uuid
import telebot
from telebot import types
import os

# Import from config
from ..config.config import bot

# Import from best time algo
from best_time_algo.best_time_algo import BestTimeAlgo

# Import from services
from services.user_service import (
    getUser,
    setUser,
    updateUserInitialised,
    updateUserCalloutCleared,
    updateUsername,
    getUserByUuid
)
from services.share_service import put_ctx
from services.event_service import (
    getEvent,
    create_event, 
    confirmEvent, 
    join_event_by_uuid, 
    generate_confirmed_event_description, 
    generate_event_description,
    get_event_availability,
    getConfirmedEvent, 
    get_event_chat
    )
from services.availability_service import ask_availability, ask_join

# Import from utils
from utils.date_utils import daterange, parse_date, format_date_for_message, format_date
from utils.web_app import create_web_app_url
from utils.message_templates import (
    WELCOME_MESSAGE, 
    EVENT_CREATED_SUCCESS, 
    GROUP_CREATE_INSTRUCTIONS
)

# Keep track of processed message IDs to prevent duplicate processing
processed_messages = set()


def register_event_handlers(bot):
    """Register all event-related handlers"""

    @bot.message_handler(commands=['create'])
    def send_welcome(message):
        tele_id = str(message.from_user.id)
        db_result = getUser(tele_id)
        if db_result is None:
            # User doesn't exist, create them
            print("User not found in DB, creating new entry.", message.from_user.id)
            username = str(message.from_user.username)
            setUser(message.from_user.id, username)
        else:
            if not db_result["initialised"]:
                updateUserInitialised(tele_id)
                updateUserCalloutCleared(tele_id)
            if db_result["tele_user"] != str(message.from_user.username):
                print("Username changed, updating in DB.")
                updateUsername(message.from_user.id, message.from_user.username)

        bot_message = bot.reply_to(message, WELCOME_MESSAGE)

        chat_id = message.chat.id
        thread_id = getattr(message, "message_thread_id", None)
        message_id = bot_message.message_id
        token = put_ctx(message.from_user.id, chat_id, message_id, thread_id)

        params = f"datepicker={token}"
        # Create web app URL for datepicker
        mini_app_url = f"https://t.me/{bot.get_me().username}/meetwhenah?startapp={params}"
        
        markup = types.InlineKeyboardMarkup()
        mini_app_button = types.InlineKeyboardButton(text="Create Event", url=mini_app_url)
        markup.add(mini_app_button)

        # Edit the same message for both private and group chats
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=WELCOME_MESSAGE,
            reply_markup=markup
        )
        return

def handle_event_creation(message, data):
    """Handle event creation from web app data"""
    try:
        # Extract event details
        event_name = data['event_name']
        event_description = data['event_details']
        start_date = data['start']
        end_date = data['end']
        start_date = parse_date(start_date)
        end_date = parse_date(end_date)
        
        print("Event details:", event_name, event_description, start_date, end_date)
        
        # Validate required fields
        if not all([event_name, event_description, start_date, end_date]):
            bot.reply_to(message, "❌ <b>Missing Information</b>\n\nMissing required event details")
            return
        
        # Create the event
        event_id = create_event(
            event_name=event_name,
            event_description=event_description,
            start_date=format_date(start_date),
            end_date=format_date(end_date),
            creator_id=str(message.from_user.id),
            auto_join=True
        )
        
        if not event_id:
            bot.reply_to(message, "❌ <b>Creation Failed</b>\n\nFailed to create event")
            return
        
        # Create share button
        markup = types.InlineKeyboardMarkup()
        
        # Add confirm button
        params = f"confirm={event_id}"
        mini_app_url = f"https://t.me/{bot.get_me().username}/meetwhenah?startapp={params}"
        confirm_button = types.InlineKeyboardButton(
            text="Confirm Best Time",
            url=mini_app_url
        )
        markup.add(confirm_button)

        event = getEvent(event_id)

        generated_description = generate_event_description(event)

        # Send confirmation message
        if message.chat.type == 'private':
            success_message = f"Event created successfully!\n\n{generated_description}\n\nShare this event with others using the /share command in your group chats! \n\nConfirm the event here when you're ready!"
        else:
            # In group chat, mention who created the event
            username = message.from_user.username or message.from_user.first_name
            success_message = f"@{username} made an event!\n\n{generated_description}\n\nShare this event with others using the /share command in your group chats! \n\nConfirm the event here when you're ready!"
        
        bot.reply_to(
            message,
            success_message,
            reply_markup=markup
        )
        
        # Ask creator for availability
        ask_availability(chat_id=message.chat.id, event_id=event_id, thread_id=None)
        
    except Exception as e:
        bot.reply_to(message, f"❌ <b>Creation Error</b>\n\nError creating event: {str(e)}")

def handle_event_confirmation(event_id, best_start_time, best_end_time):
    """Handle event confirmation from web app data"""
    print("handle_event_confirmation", event_id, best_start_time, best_end_time)
    try:
        # get event details
        event = getEvent(event_id)
        # get event creator
        creator_id = event["creator"]
        creator = getUserByUuid(creator_id)
        creator_tele_id = creator["tele_id"]

        # check if event is already confirmed
        if getConfirmedEvent(event_id):
            bot.send_message(chat_id=creator_tele_id, text=f"Event {event['event_name']} is already confirmed.")
            return
        
        # set up scheduler
        min_participants = event["min_participants"]
        min_duration_blocks = event["min_duration"]
        max_duration_blocks = event["max_duration"]
        best_time_algo = BestTimeAlgo(min_participants=min_participants, min_block_size=min_duration_blocks, max_block_size=max_duration_blocks)


        # get participants
        availability_blocks = get_event_availability(event_id)
        participants = best_time_algo.get_event_participants(availability_blocks, best_start_time, best_end_time)
        print("participants", participants)
        # Confirm the event
        success = confirmEvent(event_id, best_start_time, best_end_time)
        print("success", success)
        if not success: 
            # event failed to confirm
            message = f"Failed to confirm event {event['event_name']}."
            bot.send_message(creator_tele_id, message)
            return
        # event confirmed successfully
        print("Event confirmed successfully.")

        print("Message should be sent to creator ", creator["tele_user"])
        # add participants to event
        for participant in participants:
            success = join_event_by_uuid(event_id, participant)
            if not success:
                bot.send_message(chat_id=creator_tele_id, text=f"Failed to add participant to event.")
        print("participants", participants)
        # create share message
        description = generate_confirmed_event_description(event_id)

        text = f"Event {event['event_name']} confirmed successfully.\n\n{description}\n\nShare this event with others using the /share command in your group chats!"

        bot.send_message(chat_id=creator_tele_id, text=text)

        # send availability to event chat
        chat_id, thread_id = get_event_chat(event_id)
        if chat_id:
            ask_join(chat_id, event_id, thread_id)

    except Exception as e:
        bot.send_message(chat_id=creator_tele_id, text=f"Error confirming event: {str(e)}")
        return

