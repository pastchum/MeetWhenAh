from telebot import types
from telebot.util import quick_markup
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
import logging

logger = logging.getLogger(__name__)

def register_event_handlers(bot):
    """Register all event-related handlers"""
    
    @bot.message_handler(commands=['event'])
    def new_event(message):
        if message.chat.type == 'private':
            markup = types.ForceReply(selective=False)
            msg = bot.send_message(message.chat.id, "Please send me the name of your event:", reply_markup=markup)
            bot.register_next_step_handler(msg, event_description)
        else:
            bot.reply_to(message, "This command only works when you <i>private message</i> me!")

    def event_description(message):
        text = "Please send me the description of your event: (if any)"
        markup = quick_markup({
            'None': {'callback_data': 'yes'},
        }, row_width=1)

        msg = bot.send_message(message.chat.id, text, reply_markup=markup)
        bot.register_next_step_handler(msg, set_start_date)

    def set_start_date(message):
        bot.send_message(message.chat.id, "Now, please select the <b>Start Date</b> of your event.")
        calendar, step = DetailedTelegramCalendar().build()
        bot.send_message(message.chat.id,
                        f"Select start date",
                        reply_markup=calendar)

    def set_end_date(message):
        bot.send_message(message.chat.id, "Now, please select the <b>End Date</b> of your event.")
        calendar, step = DetailedTelegramCalendar().build()
        bot.send_message(message.chat.id,
                        f"Select end date",
                        reply_markup=calendar)

    @bot.callback_query_handler(func=DetailedTelegramCalendar.func())
    def cal(c):
        result, key, step = DetailedTelegramCalendar().process(c.data)
        if not result and key:
            bot.edit_message_text(f"Select {LSTEP[step]}",
                                c.message.chat.id,
                                c.message.message_id,
                                reply_markup=key)
        elif result:
            bot.edit_message_text(f"Saved. Date picked was {result}",
                                c.message.chat.id,
                                c.message.message_id)
            
            # Store the date and proceed with event creation
            # This will be implemented in the next step
            pass 