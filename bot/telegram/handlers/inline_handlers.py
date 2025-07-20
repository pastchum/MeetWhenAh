import telebot
from telebot import types
import logging

# Import from config
from ..config.config import bot

# Import from services
from services.event_service import getEvent, generate_event_description
from services.database_service import getEntry, setEntry, updateEntry
from services.event_service import getEventSleepPreferences, join_event
from services.user_service import updateUsername
from services.event_service import getUserAvailability, updateUserAvailability

# Import from utils
from utils.web_app import create_web_app_url
from utils.message_templates import HELP_MESSAGE

logger = logging.getLogger(__name__)

def register_inline_handlers(bot):
    """Register all inline query handlers"""
    
    @bot.inline_handler(func=lambda query: query.query.startswith("availability_"))
    def handle_inline_query(query):
        """Handle inline queries for event sharing"""
        print(query.query)
        try:
            event_id = query.query.strip().split("_")[1]
            print(event_id)
            if not event_id:
                return
            
            # Get event details
            event = getEvent(event_id)
            if not event:
                bot.answer_inline_query(query.id, [types.InlineQueryResultArticle(
                    id=event_id,
                    title="Event not found",
                    description="Event not found",
                    input_message_content=types.InputTextMessageContent(
                        message_text="Event not found"
                    )
                )])
                return
            
            description = generate_event_description(event)

            params = f"dragselector={event_id}"
            miniapp_url = f"https://t.me/{bot.get_me().username}/meetwhenah?startapp={params}"


            markup = types.InlineKeyboardMarkup()
            miniapp_btn = types.InlineKeyboardButton(
                text="Select Availability",
                url=miniapp_url
            )
            markup.add(miniapp_btn)

            # Create inline result
            result = types.InlineQueryResultArticle(
                id=event_id,
                title=f"Share: {event['event_name']}",
                description=description,
                input_message_content=types.InputTextMessageContent(
                    message_text=description
                ),
                reply_markup=markup
            )
            
            bot.answer_inline_query(query.id, [result])
            
        except Exception as e:
            logger.error(f"Error in inline query handler: {str(e)}")

    '''
    @bot.callback_query_handler(func=lambda call: call.data)
    def handle_join_callback(call):
        """Handle join event button clicks"""
        try:
            logger.info(f"Join callback data: {call.data}")
            event_id = call.data.split(':')[1]
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
                ask_availability(call.message.chat.id, event_id, username)
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
'''