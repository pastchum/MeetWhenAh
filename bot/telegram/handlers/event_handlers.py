import os
import json
from datetime import datetime, timedelta
import uuid
import telebot
from telebot import types

# Import from config
from ..config.config import bot

# Import from services
from services.user_service import updateUsername
from services.event_service import (
    create_event, 
    confirmEvent, 
    join_event, 
    generate_event_description, 
    get_event_by_id
    )
from services.availability_service import ask_availability

# Import from utils
from utils.date_utils import daterange

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
                    print("confirming event:", data)
                    #handle_event_confirmation(message, data)
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
        
        print("Event details:", event_name, event_description, start_date, end_date)
        
        # Validate required fields
        if not all([event_name, event_description, start_date, end_date]):
            bot.reply_to(message, "Missing required event details")
            return
        
        # Create the event
        event_id = create_event(
            event_name=event_name,
            event_description=event_description,
            start_date=start_date,
            end_date=end_date,
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
        params = f"confirm={event_id}"
        miniapp_url = f"https://t.me/{bot.get_me().username}/meetwhenah?startapp={params}"
        confirm_button = types.InlineKeyboardButton(
            text="Confirm Best Time",
            url=miniapp_url
        )
        markup.add(confirm_button)

        # Send confirmation message
        bot.reply_to(
            message,
            f"Event created successfully!\n\nName: {event_name}\nDetails: {event_description}\nDates: {start_date} to {end_date}\n\nShare this event with others:",
            reply_markup=markup
        )
        
        # Ask creator for availability
        ask_availability(message.chat.id, event_id)
        
    except Exception as e:
        bot.reply_to(message, f"Error creating event: {str(e)}")

def handle_event_confirmation(message, data):
    """Handle event confirmation from web app data"""
    try:
        event_id = data.get('event_id')
        best_start_time = data.get('best_start_time')
        best_end_time = data.get('best_end_time')
        participants = data.get('participants')

        # Confirm the event
        success = confirmEvent(event_id, best_start_time, best_end_time)
        if not success:
            bot.reply_to(message, "Failed to confirm event")
        else:
            bot.reply_to(message, "Event confirmed successfully")
            # add participants to event
            for participant in participants:
                success = join_event(event_id, participant)
                if not success:
                    bot.reply_to(message, f"Failed to add participant {participant} to event")
            
            # create share message
            description = generate_event_description(get_event_by_id(event_id))

            markup = types.InlineKeyboardMarkup()
            share_button = types.InlineKeyboardButton(
                text="Share Event",
                switch_inline_query=f"join_{event_id}"
            )
            markup.add(share_button)

            bot.reply_to(message, f"Event confirmed successfully!\n\n{description}", reply_markup=markup)
    except Exception as e:
        bot.reply_to(message, f"Error confirming event: {str(e)}")
        return

