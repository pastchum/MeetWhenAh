import telebot
from telebot import types
import logging

# Import from config
from ..config.config import bot

# Import from services
from services.event_service import (
    getEvent, 
    generate_event_description,
    getConfirmedEvent,
    generate_confirmed_event_description,
    generate_confirmed_event_participants_list,
    join_event,
    check_membership,
    leave_event
)

# Import from utils
from utils.web_app import create_web_app_url
from utils.message_templates import HELP_MESSAGE

logger = logging.getLogger(__name__)

def register_inline_handlers(bot):
    """Register all inline query handlers"""
    
    @bot.inline_handler(func=lambda query: query.query.startswith("availability_"))
    def handle_availability_query(query):
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

    @bot.inline_handler(func=lambda query: query.query.startswith("join_"))
    def handle_join_query(query):
        """Handle inline queries for event joining"""
        try: 
            event_id = query.query.strip().split("_")[1]
            if not event_id:
                return
            
            # Get event details
            event_confirmed = getConfirmedEvent(event_id)
            event = getEvent(event_id)
            if not event:
                not_found_result = types.InlineQueryResultArticle(
                    id=event_id,
                    title="Event not found",
                    description="Event not found",
                    input_message_content=types.InputTextMessageContent(
                        message_text="Event not found"
                    )
                )
                bot.answer_inline_query(query.id, [not_found_result])
                return
            elif not event_confirmed:
                not_found_result = types.InlineQueryResultArticle(
                    id=event_id,
                    title="Event not confirmed",
                    description="Event not confirmed",
                    input_message_content=types.InputTextMessageContent(
                        message_text="Event not confirmed"
                    )
                )
                bot.answer_inline_query(query.id, [not_found_result])
                return
            
            description = generate_confirmed_event_description(event)
            participants = generate_confirmed_event_participants_list(event)
            description += f"\n\nParticipants:\n{participants}"

            markup = types.InlineKeyboardMarkup()
            miniapp_btn = types.InlineKeyboardButton(
                text="Join Event",
                callback_data=f"join:{event_id}"
            )
            markup.add(miniapp_btn)

            result = types.InlineQueryResultArticle(
                id=event_id,
                title=f"Join: {event['event_name']}",
                description=description,
                input_message_content=types.InputTextMessageContent(
                    message_text=description
                ),
                reply_markup=markup
            )

            bot.answer_inline_query(query.id, [result])
            
        except Exception as e:
            logger.error(f"Error in inline query handler: {str(e)}")

    @bot.callback_query_handler(func=lambda call: call.data.startswith("join:"))
    def handle_join_callback(call):
        """Handle join event button clicks"""
        try:
            event_id = call.data.split(":")[1]
            tele_id = call.from_user.id
            membership_status = check_membership(event_id, tele_id)
            if membership_status:
                leave_event(event_id, tele_id)
                bot.answer_callback_query(
                    call.id,
                    f"{call.from_user.username} has left the event.",
                    show_alert=False
                )
            else:
                join_event(event_id, tele_id)
                bot.answer_callback_query(
                    call.id,
                    f"{call.from_user.username} has joined the event.",
                    show_alert=False
                )
        except Exception as e:
            logger.error(f"Error in join callback handler: {str(e)}")
            bot.answer_callback_query(
                call.id,
                "An error occurred. Please try again later.",
                show_alert=True
            )
            