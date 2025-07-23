import os
import json
from datetime import datetime, timedelta
import uuid
import telebot
from telebot import types

# Import from config
from ..config.config import bot

# Import from scheduler
from scheduler.scheduler import Scheduler

# Import from services
from services.user_service import updateUsername, getUserByUuid
from services.event_service import (
    getEvent,
    create_event, 
    confirmEvent, 
    join_event, 
    generate_confirmed_event_description, 
    generate_event_description,
    )
from services.availability_service import ask_availability

# Import from utils
from utils.date_utils import daterange, parse_date, format_date_for_message, format_date

# Keep track of processed message IDs to prevent duplicate processing
processed_messages = set()

def register_event_handlers(bot):
    """Register all event-related handlers"""

    @bot.message_handler(content_types=['web_app_data'])
    def handle_webapp_data(message):
        """Handle data received from the web app"""
        try:
            # Check if we've already processed this message
            if message.message_id in processed_messages:
                return
            processed_messages.add(message.message_id)
            
            # Keep set size manageable
            if len(processed_messages) > 1000:
                processed_messages.clear()
            
            # Parse the web app data
            if not hasattr(message, 'web_app_data') or not message.web_app_data:
                bot.send_message(message.chat.id, "Invalid web app data received.")
                return
                
            try:
                data = json.loads(message.web_app_data.data)
                web_app_number = data.get('web_app_number')
                
                if web_app_number == 0:  # Event creation
                    handle_event_creation(message, data)
                elif web_app_number == 1:
                    handle_event_confirmation(message, data)
                else:
                    bot.reply_to(message, "Invalid web app data received")
            
            except json.JSONDecodeError:
                bot.reply_to(message, "Invalid data format received from web app")
                
        except Exception as e:
            bot.reply_to(message, f"Error processing web app data: {str(e)}")

    # Return the bot instance
    return bot

def handle_event_creation(message, data):
    """Handle event creation from web app data"""
    try:
        # Extract event details
        event_name = data.get('event_name')
        event_description = data.get('event_details')
        start_date = data.get('start')
        end_date = data.get('end')
        start_date = parse_date(start_date)
        end_date = parse_date(end_date)
        
        print("Event details:", event_name, event_description, start_date, end_date)
        
        # Validate required fields
        if not all([event_name, event_description, start_date, end_date]):
            bot.reply_to(message, "Missing required event details")
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
            bot.reply_to(message, "Failed to create event")
            return
        
        # Create share button
        markup = types.InlineKeyboardMarkup()

        # Add share button
        share_button = types.InlineKeyboardButton(
            text="Share Event",
            switch_inline_query=f"availability_{event_id}"
        )
        markup.add(share_button)
        
        # Add confirm button
        params = f"event_id={event_id}"
        webapp_url = f"https://meet-when-ah.vercel.app/confirm?{params}"
        web_app_info = types.WebAppInfo(url=webapp_url)
        confirm_button = types.InlineKeyboardButton(
            text="Confirm Best Time",
            web_app=web_app_info
        )
        markup.add(confirm_button)

        event = getEvent(event_id)

        generated_description = generate_event_description(event)

        # Send confirmation message
        bot.reply_to(
            message,
            f"Event created successfully!\n\n{generated_description}\n\nShare this event with others:",
            reply_markup=markup
        )
        
        # Ask creator for availability
        ask_availability(message.chat.id, event_id)
        
    except Exception as e:
        bot.reply_to(message, f"Error creating event: {str(e)}")

def handle_event_confirmation(event_id, best_start_time, best_end_time):
    """Handle event confirmation from web app data"""
    print("handle_event_confirmation", event_id, best_start_time, best_end_time)
    try:
        # get event details
        event = getEvent(event_id)

        # set up scheduler
        min_participants = event.get("min_participants")
        min_duration_blocks = event.get("min_duration_blocks")
        max_duration_blocks = event.get("max_duration_blocks")
        scheduler = Scheduler(min_participants=min_participants, min_block_size=min_duration_blocks, max_block_size=max_duration_blocks)

        # get event creator
        creator_id = event.get("creator")
        creator = getUserByUuid(creator_id)
        creator_tele_id = creator.get("tele_id")

        # get participants
        participants = []
        #participants = scheduler.get_event_participants(event_id, best_start_time, best_end_time)

        # Confirm the event
        success = confirmEvent(event_id, best_start_time, best_end_time)
        if not success:
            message = f"Failed to confirm event {event.get('event_name')}."
            bot.send_message(creator_tele_id, message)
        else:
            print("Event confirmed successfully.")
            message = f"Event {event.get('event_name')} confirmed successfully."
            bot.send_message(chat_id=creator_tele_id, text=message)
            print("Message should be sent to creator ", creator.get("tele_user"))
            # add participants to event
            for participant in participants:
                success = join_event(event_id, participant)
                if not success:
                    bot.send_message(chat_id=creator_tele_id, text=f"Failed to add participant to event.")
            
            # create share message
            description = generate_confirmed_event_description(event)

            markup = types.InlineKeyboardMarkup()
            share_button = types.InlineKeyboardButton(
                text="Share Event",
                switch_inline_query=f"join_{event_id}"
            )
            markup.add(share_button)

            bot.send_message(chat_id=creator_tele_id, text=f"Event confirmed successfully!\n\n{description}", reply_markup=markup)
    except Exception as e:
        bot.send_message(chat_id=creator_tele_id, text=f"Error confirming event: {str(e)}")
        return

