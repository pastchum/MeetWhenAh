import telebot
from telebot import types
import logging
import re

# Import from config and services
from ..config.config import bot
from .availability_handlers import ask_availability

def register_group_handlers(bot):
    """Register all group-related handlers"""

    @bot.message_handler(func=lambda message: message.chat.type in ["group", "supergroup"])
    def handle_share_to_group(message):
        mention_pattern = rf'^@MeetWhenAhBot\s+([\w\-]+)$'
        match = re.match(mention_pattern, message.text)
        if match:
            event_id = match.group(1)
            print(event_id)
            ask_availability(message.chat.id, event_id)
        else:
            bot.reply_to(message, "Invalid event ID.")



