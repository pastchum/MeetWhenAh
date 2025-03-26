from .user_service import getEntry, setEntry, updateEntry
from datetime import datetime, timedelta

def getUserAvailability(username, event_id=None):
    """
    Get a user's global availability.
    
    Args:
        username (str): The username.
        event_id (str, optional): If provided, filters availability for event dates.
        
    Returns:
        dict: The user's availability data.
    """
    try:
        user_doc = getEntry("Users", "tele_user", username)
        if not user_doc:
            return None
            
        user_data = user_doc.to_dict()
        availability = user_data.get('global_availability', [])
        
        # If event_id is provided, filter availability for event dates
        if event_id:
            event = getEntry("Events", "event_id", event_id)
            if event:
                event_data = event.to_dict()
                start_date = event_data['start_date']
                end_date = event_data['end_date']
                
                # Filter availability to only include dates within event range
                filtered_availability = []
                for slot in availability:
                    slot_date = datetime.strptime(slot['date'], "%Y-%m-%d").date()
                    if start_date.date() <= slot_date <= end_date.date():
                        filtered_availability.append(slot)
                return filtered_availability
                
        return availability
    except Exception as e:
        print(f"Error getting user availability: {e}")
        return None

def updateUserAvailability(username, event_id=None, availability_data=None):
    """
    Update a user's global availability.
    
    Args:
        username (str): The username.
        event_id (str, optional): Not used for global availability.
        availability_data (list): List of availability data objects with date and time info.
        
    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        user_doc = getEntry("Users", "tele_user", username)
        if not user_doc:
            return False
            
        # Update the user's global availability
        doc_id = user_doc.id
        updateEntry("Users", doc_id, {'global_availability': availability_data})
        
        # If event_id is provided, also update event's hours_available
        if event_id:
            event = getEntry("Events", "event_id", event_id)
            if event:
                event_data = event.to_dict()
                hours_available = event_data.get('hours_available', [])
                
                # Update hours_available based on user's global availability
                for day in hours_available:
                    date_str = day['date'].strftime("%Y-%m-%d") if hasattr(day['date'], 'strftime') else day['date']
                    
                    # Remove user from all time slots for this day
                    for time_key, users in day.items():
                        if time_key != 'date' and username in users:
                            users.remove(username)
                    
                    # Add user to time slots based on their global availability
                    for slot in availability_data:
                        if slot['date'] == date_str:
                            time_key = slot['time']
                            if time_key in day and username not in day[time_key]:
                                day[time_key].append(username)
                
                # Update the event
                updateEntry("Events", event.id, {'hours_available': hours_available})
        
        return True
    except Exception as e:
        print(f"Error updating user availability: {e}")
        return False

def getAvailabilityForEvent(event_id):
    """
    Get all users' availability for an event based on their global availability.
    
    Args:
        event_id (str): The event ID.
        
    Returns:
        dict: A dictionary mapping dates to available users.
    """
    try:
        event = getEntry("Events", "event_id", event_id)
        if not event:
            return None
            
        event_data = event.to_dict()
        start_date = event_data['start_date']
        end_date = event_data['end_date']
        members = event_data.get('members', [])
        
        availability = {}
        for member_id in members:
            user_doc = getEntry("Users", "tele_id", member_id)
            if user_doc:
                user_data = user_doc.to_dict()
                username = user_data.get('tele_user')
                global_availability = user_data.get('global_availability', [])
                
                # Filter and add availability
                for slot in global_availability:
                    slot_date = datetime.strptime(slot['date'], "%Y-%m-%d").date()
                    if start_date.date() <= slot_date <= end_date.date():
                        date_str = slot['date']
                        time_str = slot['time']
                        
                        if date_str not in availability:
                            availability[date_str] = {}
                        if time_str not in availability[date_str]:
                            availability[date_str][time_str] = []
                            
                        availability[date_str][time_str].append(username)
        
        return availability
    except Exception as e:
        print(f"Error getting event availability: {e}")
        return None

def setUserSleepPreferences(tele_id, sleep_start, sleep_end):
    """
    Set a user's sleep preferences.
    
    Args:
        tele_id (int): The user's Telegram ID.
        sleep_start (str): Sleep start time in HHMM format.
        sleep_end (str): Sleep end time in HHMM format.
        
    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        user_doc = getEntry("Users", "tele_id", str(tele_id))
        if user_doc:
            doc_id = user_doc.id
            updateEntry("Users", doc_id, {
                "sleep_start": sleep_start,
                "sleep_end": sleep_end,
                "temp_sleep_start": None  # Clear temporary storage
            })
            return True
            
        setEntry("Users", {
            "tele_id": str(tele_id),
            "sleep_start": sleep_start,
            "sleep_end": sleep_end
        })
        return True
    except Exception as e:
        print(f"Error setting sleep preferences: {e}")
        return False 