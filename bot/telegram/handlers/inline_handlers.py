import telebot
from telebot import types
import logging

# Import from config
from ..utils.web_app import create_web_app_url
from ..services.event_service import getEvent
from ..services.database_service import getEntry, setEntry, updateEntry
from ..services.event_service import getEventSleepPreferences
from ..services.scheduling_service import join_event
from ..services.user_service import updateUsername
from ..services.event_service import getUserAvailability, updateUserAvailability
from ..services.scheduling_service import calculate_optimal_meeting_time
from ..utils.message_templates import HELP_MESSAGE

logger = logging.getLogger(__name__)

def register_inline_handlers(bot):
    """Register all inline query handlers"""
    
    @bot.inline_handler(func=lambda query: True)
    def handle_inline_query(query):
        """Handle inline queries for event sharing"""
        try:
            event_id = query.query.strip()
            if not event_id:
                return
            
            # Get event details
            event = getEvent(event_id)
            if not event:
                return
            
            # Create inline result
            result = types.InlineQueryResultArticle(
                id=event_id,
                title=f"Share: {event['name']}",
                description=event['details'],
                input_message_content=types.InputTextMessageContent(
                    message_text=f"Join event: {event['name']}\n\n{event['details']}\n\nEvent ID: {event_id}"
                ),
                reply_markup=types.InlineKeyboardMarkup().add(
                    types.InlineKeyboardButton("Join Event", callback_data=f"join_{event_id}")
                )
            )
            
            bot.answer_inline_query(query.id, [result])
            
        except Exception as e:
            logger.error(f"Error in inline query handler: {str(e)}")

    @bot.callback_query_handler(func=lambda call: call.data.startswith('join_'))
    def handle_join_callback(call):
        """Handle join event button clicks"""
        try:
            event_id = call.data.split('_')[1]
            user_id = str(call.from_user.id)
            username = call.from_user.username or user_id
            
            # Join the event
            success = join_event(event_id, user_id, username)
            
            if success:
                bot.answer_callback_query(
                    call.id,
                    "You've successfully joined the event! I'll send you a message to set your availability.",
                    show_alert=True
                )
                
                # Ask for availability
                from handlers.availability_handlers import ask_availability
                ask_availability(call.message.chat.id, event_id)
            else:
                bot.answer_callback_query(
                    call.id,
                    "Failed to join the event. Please try again later.",
                    show_alert=True
                )
                
        except Exception as e:
            logger.error(f"Error in join callback handler: {str(e)}")
            bot.answer_callback_query(
                call.id,
                "An error occurred. Please try again later.",
                show_alert=True
            )

    return bot

@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    try:
        if call.data.startswith('join:'):
            event_id = call.data.split(':')[1]
            handle_join_event(call.message, event_id, call.from_user)
        elif call.data.startswith('event:'):
            event_id = call.data.split(':')[1]
            handle_event_selection(call.message, event_id)
            
    except Exception as e:
        print(e)
        bot.answer_callback_query(call.id, "An error occurred. Please try again.")

def handle_join_event(message, event_id, user):
    event_data = getEntry("events", "event_id", event_id)
    
    if not event_data:
        bot.send_message(message.chat.id, "This event no longer exists.")
        return
        
    members = event_data.get('members', [])
    
    if str(user.id) in members:
        bot.send_message(message.chat.id, "You have already joined this event!")
        return
        
    members.append(str(user.id))
    event_data['members'] = members
    event_data['text'] = event_data['text'] + f"\n <b>{user.username}</b>"
    
    setEntry("events", event_data)
    
    # Update the original message with new member list
    try:
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=message.message_id,
            text=event_data['text'],
            reply_markup=create_join_markup(event_id),
            parse_mode='HTML'
        )
    except Exception as e:
        print(f"Failed to update message: {e}")
    
    # Send private message to user to update availability
    try:
        bot.send_message(
            user.id,
            "Please update your availability for this event:",
            reply_markup=create_availability_markup(event_id)
        )
    except Exception as e:
        print(f"Failed to send private message: {e}")

def handle_event_selection(message, event_id):
    event_data = getEntry("events", "event_id", event_id)
    
    if not event_data:
        bot.send_message(message.chat.id, "This event no longer exists.")
        return
        
    web_app_url = create_web_app_url(event_id=event_id)
    markup = types.InlineKeyboardMarkup()
    webapp_button = types.InlineKeyboardButton(
        text="Update Availability",
        web_app=types.WebAppInfo(url=web_app_url)
    )
    markup.add(webapp_button)
    
    bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=message.message_id,
        text=f"Please update your availability for this event.",
        reply_markup=markup
    )

def create_join_markup(event_id):
    markup = types.InlineKeyboardMarkup()
    join_button = types.InlineKeyboardButton(
        text="Join",
        callback_data=f"join:{event_id}"
    )
    markup.add(join_button)
    return markup

def create_availability_markup(event_id):
    web_app_url = create_web_app_url(event_id=event_id)
    markup = types.InlineKeyboardMarkup()
    webapp_button = types.InlineKeyboardButton(
        text="Update Availability",
        web_app=types.WebAppInfo(url=web_app_url)
    )
    markup.add(webapp_button)
    return markup 