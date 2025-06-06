from telebot import types
from ..config.config import bot
from ..services.database_service import getEntry
from ..services.availability_service import getUserAvailability
from ..services.scheduling_service import format_availability_summary
from ..utils.web_app import create_web_app_url
#from ..utils.native_interface import create_native_availability_selector, handle_native_availability_callback

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
    
    # Create web app URL for the drag selector
    web_app_url = create_web_app_url(
        path='/dragselector',
        web_app_number=1  # 1 for update availability
    )
    
    # Create inline keyboard with web app button
    markup = types.InlineKeyboardMarkup()
    webapp_button = types.InlineKeyboardButton(
        text="Update Your Availability",
        web_app=types.WebAppInfo(url=web_app_url)
    )
    markup.add(webapp_button)
    
    bot.send_message(
        message.chat.id,
        "Click below to update your global availability schedule:",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith(('slot_', 'save_', 'cancel_', 'date_')))
def handle_availability_callback(call):
    """Handle callbacks from the native availability selector."""
    handle_native_availability_callback(bot, call)

def get_user_events(user_id):
    """Get all events that a user is a member of."""
    try:
        events = []
        from ..services.user_service import supabase_client
        
        # Query events where user is a member
        event_data = supabase_client.from_('events').select('*').filter('members', 'cs', str(user_id)).execute()
        
        for event_data in event_data['data']:
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
    web_app_url = create_web_app_url(
        path='/dragselector',
        web_app_number=1  # 1 for update availability
    )
    markup = types.InlineKeyboardMarkup()
    webapp_button = types.InlineKeyboardButton(
        text="Update Your Global Availability",
        web_app=types.WebAppInfo(url=web_app_url)
    )
    markup.add(webapp_button)
    
    bot.send_message(
        chat_id,
        "Click below to update your global availability schedule:",
        reply_markup=markup
    ) 