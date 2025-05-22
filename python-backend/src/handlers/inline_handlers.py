from telebot import types
from ..config.config import bot
from ..services.user_service import getEntry, setEntry, updateEntry
from ..services.event_service import getEventSleepPreferences
from ..utils.web_app import create_web_app_url

@bot.inline_handler(lambda query: True)
def handle_inline_query(query):
    try:
        if ':' in query.query:
            event_name, event_id = query.query.split(':')
            event_data = getEntry("Events", "event_id", event_id)
            
            if not event_data:
                return
            text = event_data.get('text', '')
            
            r = types.InlineQueryResultArticle(
                id='1',
                title=f"Share {event_name}",
                description="Click to share this event",
                input_message_content=types.InputTextMessageContent(
                    message_text=text,
                    parse_mode='HTML'
                ),
                reply_markup=create_join_markup(event_id)
            )
            bot.answer_inline_query(query.id, [r])
        else:
            # Handle empty query or search functionality
            pass
            
    except Exception as e:
        print(e)

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
    event_data = getEntry("Events", "event_id", event_id)
    
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
    
    setEntry("Events", event_data)
    
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
    event_data = getEntry("Events", "event_id", event_id)
    
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