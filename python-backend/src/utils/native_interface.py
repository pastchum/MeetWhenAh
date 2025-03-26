# from telebot import types
# from datetime import datetime, timedelta
# from ..services.availability_service import getUserAvailability, updateUserAvailability
# from ..services.user_service import getEntry

"""
Native interface implementation (commented out for now)

def create_native_availability_selector(bot, message, event_id, event_data):
    # Get current availability
    current_availability = getUserAvailability(message.from_user.username, event_id)
    
    # Create message text
    text = f"📅 Select your availability for: {event_data['event_name']}\n\n"
    text += "🕒 Click time slots to toggle your availability\n"
    text += "✅ Selected slots will be marked with a checkmark\n"
    text += "🔒 Occupied slots are marked with a lock\n\n"
    
    # Create inline keyboard
    markup = types.InlineKeyboardMarkup(row_width=6)  # Increased row width for more slots per row
    
    # Get date range - ensure at least 3 weeks
    start_date = event_data['start_date']
    end_date = max(event_data['end_date'], start_date + timedelta(weeks=3))
    
    # Create time slots (12 AM to 12 PM, 30-min intervals)
    time_slots = []
    for hour in range(24):  # 0-23 hours
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
        
        # Get occupied slots for this date
        occupied_slots = set()
        event = getEntry("Events", "event_id", event_id)
        if event:
            event_dict = event.to_dict()
            for day in event_dict.get('hours_available', []):
                if hasattr(day['date'], 'strftime'):
                    day_str = day['date'].strftime("%Y-%m-%d")
                else:
                    day_str = day['date']
                if day_str == date_str:
                    for time_key, users in day.items():
                        if time_key != 'date' and len(users) > 0:
                            occupied_slots.add(time_key)
        
        # Add time slot buttons in rows of 6
        row = []
        for time in time_slots:
            # Check if this slot is selected by the user
            is_selected = False
            if current_availability:
                for slot in current_availability:
                    if slot["date"] == date_str and slot["time"] == time:
                        is_selected = True
                        break
            
            # Check if slot is occupied
            is_occupied = time in occupied_slots
            
            # Format time for display (e.g., "00:00" or "14:30")
            display_time = f"{time[:2]}:{time[2:]}"
            
            # Add appropriate indicator
            if is_selected:
                button_text = f"{display_time} ✅"
            elif is_occupied:
                button_text = f"{display_time} 🔒"
            else:
                button_text = display_time
            
            row.append(types.InlineKeyboardButton(
                text=button_text,
                callback_data=f"slot_{date_str}_{time}"
            ))
            
            # Add row when it has 6 buttons
            if len(row) == 6:
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
    try:
        action, *data = call.data.split('_')
        
        if action == "date":
            # Date headers are non-functional
            bot.answer_callback_query(call.id)
            return
            
        elif action == "slot":
            date_str, time = data
            username = call.from_user.username
            event_id = call.message.text.split(': ')[1].split('\n')[0]
            
            # Get event to check if slot is occupied
            event = getEntry("Events", "event_id", event_id)
            if event:
                event_dict = event.to_dict()
                for day in event_dict.get('hours_available', []):
                    if hasattr(day['date'], 'strftime'):
                        day_str = day['date'].strftime("%Y-%m-%d")
                    else:
                        day_str = day['date']
                    if day_str == date_str and time in day and len(day[time]) > 0:
                        bot.answer_callback_query(call.id, text="⚠️ This slot is occupied!")
                        return
            
            # Get current availability
            current_availability = getUserAvailability(username, event_id)
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
            updateUserAvailability(username, event_id, current_availability)
            
            # Get event data to recreate the markup
            event_data = {
                'event_name': event_id,
                'start_date': datetime.strptime(date_str, "%Y-%m-%d"),
                'end_date': datetime.strptime(date_str, "%Y-%m-%d") + timedelta(weeks=3)
            }
            
            # Update the message with new selection
            text, markup = create_native_availability_selector(bot, call.message, event_id, event_data)
            bot.edit_message_text(
                text=text,
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=markup,
                parse_mode='HTML'
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
""" 