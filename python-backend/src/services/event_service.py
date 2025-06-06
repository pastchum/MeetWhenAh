from datetime import datetime, timedelta
from typing import Dict, List, Optional
from utils.date_utils import daterange
from services.database_service import getEntry, setEntry, updateEntry

def getEvent(event_id: str) -> Optional[Dict]:
    """Get event details by ID"""
    event = getEntry("Events", "event_id", event_id)
    return event if event else None

def getEventSleepPreferences(event_id: str) -> Dict[str, Dict[str, int]]:
    """Get sleep preferences for all participants in an event"""
    event = getEntry("Events", "event_id", event_id)
    if not event:
        return {}
    
    sleep_prefs = {}
    for user_id in event.get("participants", []):
        user = getEntry("Users", "user_id", user_id)
        if user and "sleep_start" in user and "sleep_end" in user:
            sleep_prefs[user_id] = {
                "start": user["sleep_start"],
                "end": user["sleep_end"]
            }
    
    return sleep_prefs

def getUserAvailability(username: str, event_id: str) -> List[Dict]:
    """Get a user's availability for an event"""
    availability = getEntry("Availability", "event_id", event_id)
    if not availability:
        return []
    
    user_availability = availability.get(username, [])
    return user_availability

def updateUserAvailability(username: str, event_id: str, availability_data: List[Dict]) -> bool:
    """Update a user's availability for an event"""
    availability = getEntry("Availability", "event_id", event_id)
    
    if availability:
        # Update existing availability
        availability_data = availability.copy()
        availability_data[username] = availability_data
        availability_data["updated_at"] = datetime.now()
        return updateEntry("Availability", event_id, availability_data)
    else:
        # Create new availability
        availability_data = {
            "event_id": event_id,
            username: availability_data,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        return setEntry("Availability", event_id, availability_data)

def calculateBestTimes(event_id):
    """
    Calculate the best times for an event based on member availability.
    
    Args:
        event_id (str): The event ID.
        
    Returns:
        tuple: A tuple of (best_date, best_time).
    """
    try:
        event_data = getEntry("events", "event_id", event_id)
        if not event_data:
            return None, None
            
        hours_available = event_data.get('hours_available', [])
        members = event_data.get('members', [])
        
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