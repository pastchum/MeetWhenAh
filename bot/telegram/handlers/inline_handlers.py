import telebot
from telebot import types
import logging

# Import from config
from ..config.config import bot
from ..utils.web_app import create_web_app_url
from ..services.event_service import getEvent
from ..services.database_service import getEntry, setEntry, updateEntry
from ..services.event_service import getEventSleepPreferences, join_event
from ..services.user_service import updateUsername
from ..services.event_service import getUserAvailability, updateUserAvailability
from ..services.scheduling_service import calculate_optimal_meeting_time
from ..utils.message_templates import HELP_MESSAGE
from telebot.apihelper import ApiTelegramException

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
                    message_text=f"Join event: {event['name']}\n\n{event['details']}\n\nEvent ID: {event_id}\n\n" +
                    "📌 **IMPORTANT**: In groups with topics, you MUST reply to a message in your target topic when sharing."
                ),
                reply_markup=types.InlineKeyboardMarkup().add(
                    types.InlineKeyboardButton("Join Event", callback_data=f"join:{event_id}")
                )
            )
            
            bot.answer_inline_query(query.id, [result])
            
        except Exception as e:
            logger.error(f"Error in inline query handler: {str(e)}")

    @bot.callback_query_handler(func=lambda call: call.data and (call.data.startswith('join:') or call.data.startswith('join_')))
    def handle_join_callback(call):
        """Handle join event button clicks"""
        try:
            logger.info(f"JOIN CALLBACK via registered handler: {call.data}")
            logger.info(f"Message details: thread_id={getattr(call.message, 'message_thread_id', None)}, chat_id={call.message.chat.id}")
            
            # Handle both formats
            event_id = call.data.split(':')[1] if ':' in call.data else call.data.split('_')[1]
            
            # Call the existing handle_join_event function
            handle_join_event(call.message, event_id, call.from_user)
                
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
        logger.info(f"Callback received: {call.data}, message_thread_id={getattr(call.message, 'message_thread_id', None)}")
        
        # Handle both formats for maximum compatibility
        if call.data.startswith('join:') or call.data.startswith('join_'):
            # Extract event_id regardless of separator
            event_id = call.data.split(':')[1] if ':' in call.data else call.data.split('_')[1]
            handle_join_event(call.message, event_id, call.from_user)
        elif call.data.startswith('event:'):
            event_id = call.data.split(':')[1]
            handle_event_selection(call.message, event_id)
            
    except Exception as e:
        logger.error(f"Error in callback handler: {str(e)}")
        logger.exception("Detailed error:")
        bot.answer_callback_query(call.id, "An error occurred. Please try again.")

def handle_join_event(message, event_id, user):
    # Debug log for topic info
    logger.info(f"Handling join event: event_id={event_id}, chat_id={message.chat.id}, thread_id={getattr(message, 'message_thread_id', None)}")
    
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
            parse_mode='HTML',
            message_thread_id=getattr(message, 'message_thread_id', None)  # Use thread if present
        )
        # Store thread info for future updates
        event_data['chat_id'] = message.chat.id
        event_data['message_id'] = message.message_id
        event_data['message_thread_id'] = getattr(message, 'message_thread_id', None)
        setEntry("events", event_data)
    except ApiTelegramException as e:
        if 'TOPIC_CLOSED' in str(e) or 'BAD_REQUEST' in str(e):
            # Notify user and post new message in General topic
            bot.send_message(
                message.chat.id,
                "The topic for this event was closed or deleted. Posting a new event message in the General topic.",
                reply_to_message_id=message.message_id
            )
            new_msg = bot.send_message(
                message.chat.id,
                event_data['text'],
                reply_markup=create_join_markup(event_id),
                parse_mode='HTML'
                # Omit message_thread_id to post in General
            )
            # Store new message info
            event_data['chat_id'] = new_msg.chat.id
            event_data['message_id'] = new_msg.message_id
            event_data['message_thread_id'] = None
            setEntry("events", event_data)
        else:
            raise
    
    # Send private message to user to update availability
    try:
        username = user.username or str(user.id)
        bot.send_message(
            user.id,
            "Please update your availability for this event:",
            reply_markup=create_availability_markup(event_id, username)
        )
    except Exception as e:
        print(f"Failed to send private message: {e}")

def handle_event_selection(message, event_id):
    event_data = getEntry("events", "event_id", event_id)
    
    if not event_data:
        bot.send_message(message.chat.id, "This event no longer exists.")
        return
    
    # Get username from the user who clicked the button
    username = message.from_user.username or str(message.from_user.id)
        
    web_app_url = create_web_app_url("/dragselector", 1, event_id=event_id, username=username)
    markup = types.InlineKeyboardMarkup()
    webapp_button = types.InlineKeyboardButton(
        text="Update Availability",
        web_app=types.WebAppInfo(url=web_app_url)
    )
    markup.add(webapp_button)
    
    try:
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=message.message_id,
            text=f"Please update your availability for this event.",
            reply_markup=markup,
            message_thread_id=getattr(message, 'message_thread_id', None) # Use thread if present
        )
        # Store thread info for future updates
        event_data['chat_id'] = message.chat.id
        event_data['message_id'] = message.message_id
        event_data['message_thread_id'] = getattr(message, 'message_thread_id', None)
        setEntry("events", event_data)
    except ApiTelegramException as e:
        if 'TOPIC_CLOSED' in str(e) or 'BAD_REQUEST' in str(e):
            # Notify user and post new message in General topic
            bot.send_message(
                message.chat.id,
                "The topic for this event was closed or deleted. Posting a new event message in the General topic.",
                reply_to_message_id=message.message_id
            )
            new_msg = bot.send_message(
                message.chat.id,
                f"Please update your availability for this event.",
                reply_markup=markup
            )
            # Store new message info
            event_data['chat_id'] = new_msg.chat.id
            event_data['message_id'] = new_msg.message_id
            event_data['message_thread_id'] = None
            setEntry("events", event_data)
        else:
            raise

def create_join_markup(event_id):
    markup = types.InlineKeyboardMarkup()
    join_button = types.InlineKeyboardButton(
        text="Join",
        callback_data=f"join:{event_id}"
    )
    markup.add(join_button)
    return markup

def create_availability_markup(event_id, username=None):
    # If username is not provided, we can't create a proper URL for group contexts
    # This function should be called with a username parameter
    if not username:
        # Fallback - create a generic URL (this should be avoided in group contexts)
        web_app_url = create_web_app_url("/dragselector", 1, event_id=event_id)
    else:
        web_app_url = create_web_app_url("/dragselector", 1, event_id=event_id, username=username)
    
    markup = types.InlineKeyboardMarkup()
    webapp_button = types.InlineKeyboardButton(
        text="Update Availability",
        web_app=types.WebAppInfo(url=web_app_url)
    )
    markup.add(webapp_button)
    return markup 