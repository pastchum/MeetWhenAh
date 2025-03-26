from telebot import types
from datetime import datetime, timedelta
import json

def create_native_availability_selector(bot, message, event_id, event_data):
    """
    Create a native Telegram interface for selecting availability.
    This is optimized for mobile users.
    """
    # Get current availability
    current_availability = getUserAvailability(message.from_user.username, event_id)
    
    # Create a message with time slots
    text = f"Select your availability for {event_data['event_name']}\n\n"
    text += "Click on time slots to toggle them. Selected slots will be marked with ✅\n\n"
    
    # Create inline keyboard with time slots
    markup = types.InlineKeyboardMarkup(row_width=4)
    
    # Add day headers
    days = []
    current_date = event_data['start_date']
    while current_date <= event_data['end_date']:
        days.append(current_date)
        current_date += timedelta(days=1)
    
    # Create time slots (every 30 minutes from 9 AM to 9 PM)
    time_slots = []
    for hour in range(9, 22):  # 9 AM to 9 PM
        time_slots.extend([
            f"{hour:02d}:00",
            f"{hour:02d}:30"
        ])
    
    # Add time slot buttons
    for day in days:
        day_str = day.strftime("%Y-%m-%d")
        day_display = day.strftime("%a, %b %d")
        
        # Add day header
        markup.add(types.InlineKeyboardButton(day_display, callback_data=f"Day_{day_str}"))
        
        # Add time slots for this day
        for time in time_slots:
            # Check if this slot is currently selected
            is_selected = False
            if current_availability:
                for slot in current_availability:
                    if slot["date"] == day_str and slot["time"] == time.replace(":", ""):
                        is_selected = True
                        break
            
            # Create button with appropriate text and callback data
            button_text = f"{time}{' ✅' if is_selected else ''}"
            callback_data = f"Slot_{day_str}_{time.replace(':', '')}"
            markup.add(types.InlineKeyboardButton(button_text, callback_data=callback_data))
    
    # Add control buttons
    markup.add(
        types.InlineKeyboardButton("Save", callback_data=f"Save_{event_id}"),
        types.InlineKeyboardButton("Cancel", callback_data=f"Cancel_{event_id}")
    )
    
    return text, markup

def handle_native_availability_callback(bot, call):
    """
    Handle callbacks from the native availability selector
    """
    data = call.data.split("_")
    action = data[0]
    
    if action == "Slot":
        # Toggle time slot
        day = data[1]
        time = data[2]
        
        # Get current availability
        current_availability = getUserAvailability(call.from_user.username, event_id)
        
        # Check if slot is already selected
        slot_exists = False
        if current_availability:
            for slot in current_availability:
                if slot["date"] == day and slot["time"] == time:
                    slot_exists = True
                    break
        
        # Update availability
        if slot_exists:
            # Remove slot
            current_availability = [slot for slot in current_availability 
                                 if not (slot["date"] == day and slot["time"] == time)]
        else:
            # Add slot
            if not current_availability:
                current_availability = []
            current_availability.append({"date": day, "time": time})
        
        # Update in database
        updateUserAvailability(call.from_user.username, event_id, current_availability)
        
        # Update the message with new selection
        text, markup = create_native_availability_selector(bot, call.message, event_id, event_data)
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)
        
    elif action == "Save":
        # Save changes and close selector
        event_id = data[1]
        bot.edit_message_text(
            "Your availability has been saved!",
            call.message.chat.id,
            call.message.message_id
        )
        
    elif action == "Cancel":
        # Cancel changes and close selector
        event_id = data[1]
        bot.edit_message_text(
            "Changes cancelled.",
            call.message.chat.id,
            call.message.message_id
        ) 