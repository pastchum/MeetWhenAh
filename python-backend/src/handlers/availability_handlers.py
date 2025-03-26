from telebot import types
from ..config.config import bot
from ..services.user_service import getEntry
from ..services.availability_service import getUserAvailability
from ..services.scheduling_service import format_availability_summary
from ..utils.web_app import create_web_app_url

@bot.message_handler(commands=['myavailability'])
def check_availability(message):
    """Handle the /myavailability command."""
    markup = types.ForceReply(selective=False)
    bot.send_message(
        message.chat.id,
        "Please enter the event ID to check your availability:",
        reply_markup=markup
    )
    bot.register_next_step_handler(message, process_check_availability)

def process_check_availability(message):
    """Process the event ID and show user's availability."""
    try:
        event_id = message.text.strip()
        username = message.from_user.username
        
        availability = getUserAvailability(username, event_id)
        if not availability:
            bot.send_message(
                message.chat.id,
                "Could not find this event or you haven't set your availability yet."
            )
            return
            
        summary = format_availability_summary(availability)
        bot.send_message(message.chat.id, f"Your availability:\n\n{summary}")
        
    except Exception as e:
        print(f"Error checking availability: {e}")
        bot.send_message(
            message.chat.id,
            "An error occurred while checking your availability. Please try again."
        )

@bot.message_handler(commands=['updateavailability'])
def update_availability(message):
    """Handle the /updateavailability command."""
    if message.chat.type != 'private':
        bot.reply_to(message, "This command only works in private chat. Please message me directly.")
        return
        
    # Get user's events
    user_id = str(message.from_user.id)
    events = get_user_events(user_id)
    
    if not events:
        bot.send_message(
            message.chat.id,
            "You are not a member of any events. Join an event first!"
        )
        return
        
    # Create inline keyboard with events
    markup = types.InlineKeyboardMarkup(row_width=1)
    for event in events:
        button = types.InlineKeyboardButton(
            text=event['name'],
            callback_data=f"event:{event['id']}"
        )
        markup.add(button)
        
    bot.send_message(
        message.chat.id,
        "Select an event to update your availability:",
        reply_markup=markup
    )

def get_user_events(user_id):
    """Get all events that a user is a member of."""
    try:
        events = []
        event_docs = bot.firestore_client.collection('Events').where('members', 'array_contains', user_id).stream()
        
        for doc in event_docs:
            event_data = doc.to_dict()
            events.append({
                'id': event_data.get('event_id'),
                'name': event_data.get('event_name', 'Unnamed Event')
            })
            
        return events
    except Exception as e:
        print(f"Error getting user events: {e}")
        return []

def ask_availability(chat_id, event_id):
    """Ask a user to update their availability for an event."""
    web_app_url = create_web_app_url(event_id=event_id)
    markup = types.InlineKeyboardMarkup()
    webapp_button = types.InlineKeyboardButton(
        text="Update Availability",
        web_app=types.WebAppInfo(url=web_app_url)
    )
    markup.add(webapp_button)
    
    bot.send_message(
        chat_id,
        "Please update your availability for this event:",
        reply_markup=markup
    ) 