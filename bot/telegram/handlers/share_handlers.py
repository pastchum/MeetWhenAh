from telebot import types
import logging
import os

# Import from config
from ..config.config import bot

# Import from services
from services.share_service import put_ctx

# Import from other
import uuid

logger = logging.getLogger(__name__)

PAGE_SIZE = 10

bot_username = bot.get_me().username

print(f"Bot username: {bot_username}")

def register_share_handlers(bot):
    """Register all share handlers"""

    @bot.message_handler(commands=['share'])
    def handle_share_command(message):
            """Handle /share command -> prompt to pick an event inline"""
            chat_id = message.chat.id
            thread_id = getattr(message, "message_thread_id", None)

            sent_message = bot.send_message(
                chat_id=chat_id,
                message_thread_id=thread_id,
                text="Please select an event to share in this chat.",
                reply_markup=markup
            )

            token = put_ctx(message.from_user.id, chat_id, sent_message.message_id, thread_id)

            params = f"share_{token}"
            miniapp_url = f"https://t.me/{bot_username}?start={params}"

            markup = types.InlineKeyboardMarkup()
            markup.add(
                types.InlineKeyboardButton(
                    text="Select Event",
                    url=miniapp_url
                )
            )
            bot.edit_message_text(
                chat_id=chat_id,
                message_thread_id=thread_id,
                message_id=sent_message.message_id,
                text="Select an event to share in this chat.",
                reply_markup=markup
            )
