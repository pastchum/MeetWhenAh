from telebot import types
from datetime import datetime, timedelta

# Import from services
from .event_service import getUserAvailability, updateUserAvailability

def create_native_availability_selector(bot, message, event_id, event_data):
    """
    Create a native Telegram interface for selecting availability.
    Returns a tuple of (message_text, inline_keyboard_markup)
    """
    # Get current availability
    current_availability = getUserAvailability(message.from_user.username, event_id)
    
    # Create message text
    text = f"📅 Select your availability for: {event_data['event_name']}\n\n"
    text += "🕒 Click time slots to toggle your availability\n"
    text += "✅ Selected slots will be marked with a checkmark\n\n"
    
    # Create inline keyboard
    markup = types.InlineKeyboardMarkup(row_width=4)
    
    # Get date range
    start_date = event_data['start_date']
    end_date = event_data['end_date']
    
    # Create time slots (9 AM to 9 PM, 30-min intervals)
    time_slots = []
    for hour in range(9, 22):  # 9 AM to 9 PM
        time_slots.extend([f"{hour:02d}00", f"{hour:02d}30"])
    
    # Add buttons for each day and its time slots
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime("%Y-%m-%d")
        
        # Add date header button (full width)
        date_header = current_date.strftime("%a, %b %d")  # e.g., "Mon, Mar 25"
        markup.add(types.InlineKeyboardButton(
            text=f"📅 {date_header}",
            callback_data=f"date_{date_str}"  # Non-functional button, just for display
        ))
        
        # Add time slot buttons in rows of 4
        row = []
        for time in time_slots:
            # Check if this slot is selected
            is_selected = False
            if current_availability:
                for slot in current_availability:
                    if slot["date"] == date_str and slot["time"] == time:
                        is_selected = True
                        break
            
            # Format time for display (e.g., "09:00" or "14:30")
            display_time = f"{time[:2]}:{time[2:]}"
            button_text = f"{display_time} {'✅' if is_selected else ''}"
            
            row.append(types.InlineKeyboardButton(
                text=button_text,
                callback_data=f"slot_{date_str}_{time}"
            ))
            
            # Add row when it has 4 buttons
            if len(row) == 4:
                markup.add(*row)
                row = []
        
        # Add any remaining buttons in the last row
        if row:
            markup.add(*row)
        
        current_date += timedelta(days=1)
    
    # Add control buttons at the bottom
    markup.add(
        types.InlineKeyboardButton("💾 Save", callback_data=f"save_{event_id}"),
        types.InlineKeyboardButton("❌ Cancel", callback_data=f"cancel_{event_id}")
    )
    
    return text, markup

def handle_native_availability_callback(bot, call):
    """Handle callbacks from the native availability selector."""
    try:
        action, *data = call.data.split('_')
        
        if action == "date":
            # Date headers are non-functional
            bot.answer_callback_query(call.id)
            return
            
        elif action == "slot":
            date_str, time = data
            username = call.from_user.username
            
            # Get current availability
            current_availability = getUserAvailability(username, call.message.text.split(': ')[1].split('\n')[0])
            if not current_availability:
                current_availability = []
            
            # Find if this slot is already selected
            slot_exists = False
            for slot in current_availability:
                if slot["date"] == date_str and slot["time"] == time:
                    slot_exists = True
                    current_availability.remove(slot)
                    break
            
            # If slot wasn't found, add it
            if not slot_exists:
                current_availability.append({"date": date_str, "time": time})
            
            # Update availability in database
            updateUserAvailability(username, call.message.text.split(': ')[1].split('\n')[0], current_availability)
            
            # Get event data to recreate the markup
            event_data = {
                'event_name': call.message.text.split(': ')[1].split('\n')[0],
                'start_date': datetime.strptime(date_str, "%Y-%m-%d"),
                'end_date': datetime.strptime(date_str, "%Y-%m-%d")
            }
            
            # Update the message with new selection
            text, markup = create_native_availability_selector(bot, call.message, call.message.text.split(': ')[1].split('\n')[0], event_data)
            bot.edit_message_text(
                text=text,
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=markup
            )
            
            bot.answer_callback_query(call.id, text="✅ Updated!")
            
        elif action == "save":
            bot.edit_message_text(
                text="✅ Your availability has been saved!",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id
            )
            bot.answer_callback_query(call.id, text="Saved successfully!")
            
        elif action == "cancel":
            bot.edit_message_text(
                text="❌ Availability update cancelled.",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id
            )
            bot.answer_callback_query(call.id, text="Cancelled!")
            
    except Exception as e:
        print(f"Error handling availability callback: {e}")
        bot.answer_callback_query(call.id, text="❌ An error occurred!") 