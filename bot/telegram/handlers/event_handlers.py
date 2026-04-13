from bot.events.events import Event
from telebot import types

# Import from config
from ..config.config import bot

from services.user_service import getUser, getUserFromUuid, setUser, updateUsername, updateUserInitialised
from services.share_service import put_ctx
from services.membership_service import join_event_by_uuid
from services.event_service import (
    generate_confirmed_event_description,
    getConfirmedEvent,
    get_event_chat
    )
from services.availability_service import ask_availability, ask_join

# Import from utils
from utils.date_utils import parse_date
from utils.message_templates import (
    WELCOME_MESSAGE,
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
            setUser(tele_id, username)
        else:
            if not db_result["initialised"]:
                updateUserInitialised(tele_id)
            if db_result["tele_user"] != str(message.from_user.username):
                print("Username changed, updating in DB.")
                updateUsername(tele_id, str(message.from_user.username))

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
        event = Event.create_event(
            event_name=event_name,
            event_description=event_description,
            start_date=start_date,
            end_date=end_date,
            creator_id=str(message.from_user.id),
            auto_join=True
        )

        if not event:
            bot.reply_to(message, "❌ <b>Creation Failed</b>\n\nFailed to create event")
            return
        
        # Create share button
        markup = types.InlineKeyboardMarkup()

        event_id = event.get_event_id()
        
        # Add confirm button
        params = f"confirm={event_id}"
        mini_app_url = f"https://t.me/{bot.get_me().username}/meetwhenah?startapp={params}"
        confirm_button = types.InlineKeyboardButton(
            text="Confirm Best Time",
            url=mini_app_url
        )
        markup.add(confirm_button)

        generated_description = event.get_event_details_for_message()

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
        event = Event.get_event(event_id)
        if not event:
            raise Exception("Event not found")
        # get event creator
        creator_id = event.get_creator()
        creator = getUserFromUuid(creator_id)
        creator_tele_id = creator["tele_id"]

        # check if event is already confirmed
        if getConfirmedEvent(event_id):
            bot.send_message(chat_id=creator_tele_id, text=f"Event {event['event_name']} is already confirmed.")
            return
        
        # check time validity
        best_start_time = parse_date(best_start_time)
        best_end_time = parse_date(best_end_time)
        print("best time", best_start_time, best_end_time)
        if best_start_time >= best_end_time:
            bot.send_message(chat_id=creator_tele_id, text=f"Invalid best time range selected.")
            return

        # get participants
        participants = event.get_users_from_timings(best_start_time, best_end_time)
        print("participants", participants)
        # Confirm the event
        success = event.confirmEvent(best_start_time, best_end_time)
        print("success", success)
        if not success: 
            # event failed to confirm
            message = f"Failed to confirm event {event.get_event_name()}."
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

