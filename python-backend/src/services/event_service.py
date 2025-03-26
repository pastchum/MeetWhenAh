from datetime import datetime, timedelta
from .user_service import getEntry, setEntry, updateEntry
from ..utils.date_utils import daterange

def getEventSleepPreferences(event_id):
    """
    Get sleep preferences for all members of an event.
    
    Args:
        event_id (str): The event ID.
        
    Returns:
        list: A list of tuples (username, sleep_start, sleep_end).
    """
    try:
        event = getEntry("Events", "event_id", event_id)
        if not event:
            return []
            
        event_dict = event.to_dict()
        members = event_dict.get('members', [])
        
        sleep_prefs = []
        for member_id in members:
            user_doc = getEntry("Users", "tele_id", member_id)
            if user_doc:
                user_data = user_doc.to_dict()
                sleep_prefs.append((
                    user_data.get('tele_user'),
                    user_data.get('sleep_start'),
                    user_data.get('sleep_end')
                ))
                
        return sleep_prefs
    except Exception as e:
        print(f"Error getting event sleep preferences: {e}")
        return []

def getUserAvailability(username, event_id):
    """
    Get a user's availability for an event.
    
    Args:
        username (str): The username.
        event_id (str): The event ID.
        
    Returns:
        dict: The user's availability data.
    """
    try:
        event = getEntry("Events", "event_id", event_id)
        if not event:
            return None
            
        event_dict = event.to_dict()
        hours_available = event_dict.get('hours_available', [])
        
        user_availability = []
        for day in hours_available:
            day_data = {
                'date': day['date'],
                'times': []
            }
            for time, users in day.items():
                if time != 'date' and username in users:
                    day_data['times'].append(time)
            user_availability.append(day_data)
            
        return user_availability
    except Exception as e:
        print(f"Error getting user availability: {e}")
        return None

def updateUserAvailability(username, event_id, new_availability):
    """
    Update a user's availability for an event.
    
    Args:
        username (str): The username.
        event_id (str): The event ID.
        new_availability (list): List of dictionaries with date and times.
        
    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        event = getEntry("Events", "event_id", event_id)
        if not event:
            return False
            
        event_dict = event.to_dict()
        hours_available = event_dict.get('hours_available', [])
        
        # Create a mapping of dates to times for quick lookup
        availability_map = {}
        for day in new_availability:
            availability_map[day['date']] = set(day['times'])
            
        # Update the hours_available data
        for day in hours_available:
            date = day['date']
            if date in availability_map:
                new_times = availability_map[date]
                # Remove user from times not in new_times
                for time, users in day.items():
                    if time != 'date':
                        if time not in new_times and username in users:
                            users.remove(username)
                        elif time in new_times and username not in users:
                            users.append(username)
                            
        # Update the event document
        doc_id = event.id
        updateEntry("Events", doc_id, {'hours_available': hours_available})
        return True
    except Exception as e:
        print(f"Error updating user availability: {e}")
        return False

def calculateBestTimes(event_id):
    """
    Calculate the best times for an event based on member availability.
    
    Args:
        event_id (str): The event ID.
        
    Returns:
        tuple: A tuple of (best_date, best_time).
    """
    try:
        event = getEntry("Events", "event_id", event_id)
        if not event:
            return None, None
            
        event_dict = event.to_dict()
        hours_available = event_dict.get('hours_available', [])
        members = event_dict.get('members', [])
        
        if not members:
            return None, None
            
        best_count = 0
        best_date = None
        best_time = None
        
        for day in hours_available:
            date = day['date']
            for time, users in day.items():
                if time != 'date':
                    count = len(users)
                    if count > best_count:
                        best_count = count
                        best_date = date
                        best_time = time
                        
        return best_date, best_time
    except Exception as e:
        print(f"Error calculating best times: {e}")
        return None, None 