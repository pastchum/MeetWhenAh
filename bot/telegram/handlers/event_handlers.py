import os
import json
from datetime import datetime, timedelta
import uuid
import telebot
from telebot import types

# Import from config
from ..config.config import bot
from ..utils.web_app import create_web_app_url
from ..services.scheduling_service import create_event, get_event_by_id, join_event
from ..services.database_service import getEntry, setEntry, updateEntry
from ..services.user_service import updateUsername
from ..services.event_service import getEventSleepPreferences, getUserAvailability, updateUserAvailability
from ..services.scheduling_service import calculate_optimal_meeting_time
from ..utils.date_utils import daterange
from .availability_handlers import ask_availability

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
                
                if web_app_number == 1:  # Event creation
                    handle_event_creation(message, data)
                elif web_app_number == 2:  # Availability update
                    handle_availability_update(message, data)
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
        name = data.get('name')
        details = data.get('details')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        # Validate required fields
        if not all([name, details, start_date, end_date]):
            bot.reply_to(message, "Missing required event details")
            return
        
        # Create the event
        event_id = create_event(
            name=name,
            details=details,
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
        share_button = types.InlineKeyboardButton(
            text="Share Event",
            switch_inline_query=event_id
        )
        markup.add(share_button)
        
        # Send confirmation message
        bot.reply_to(
            message,
            f"Event created successfully!\n\nName: {name}\nDetails: {details}\nDates: {start_date} to {end_date}\n\nShare this event with others:",
            reply_markup=markup
        )
        
        # Ask creator for availability
        ask_availability(message.chat.id, event_id)
        
    except Exception as e:
        bot.reply_to(message, f"Error creating event: {str(e)}")

def handle_availability_update(message, data):
    """Handle availability update from web app data"""
    try:
        # Extract availability details
        event_id = data.get('event_id')
        availability_data = data.get('availability')
        username = message.from_user.username or str(message.from_user.id)
        
        # Update username in database
        updateUsername(str(message.from_user.id), username)
        
        # Update availability
        success = updateUserAvailability(username, event_id, availability_data)
        
        if success:
            bot.reply_to(message, "Your availability has been updated successfully!")
            
            # Get event details
            event = get_event_by_id(event_id)
            if event and len(event.get('participants', [])) > 1:
                # Calculate optimal meeting time
                hours_available = getUserAvailability(username, event_id)
                sleep_prefs = getEventSleepPreferences(event_id)
                optimal_time = calculate_optimal_meeting_time(hours_available, sleep_prefs)
                
                if optimal_time.get('max_participants', 0) > 0:
                    bot.reply_to(
                        message,
                        f"Based on everyone's availability, the best meeting time would be:\n"
                        f"Date: {optimal_time['final_date']}\n"
                        f"Time: {optimal_time['final_start_timing']}-{optimal_time['final_end_timing']}\n"
                        f"Participants available: {optimal_time['max_participants']}"
                    )
        else:
            bot.reply_to(message, "Failed to update your availability")
            
    except Exception as e:
        bot.reply_to(message, f"Error updating availability: {str(e)}")

def create_hours_available(start_date, end_date):
    """Create hours available structure"""
    hours_available = []
    for date in daterange(start_date, end_date):
        hours_available.append({
            'date': date.strftime('%Y-%m-%d'),
            'hours': []
        })
    return hours_available

def create_event_text(start_date, end_date):
    """Create event text for sharing"""
    return f"New event from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}" 