from datetime import datetime
from typing import Dict, List, Optional
from .database_service import getEntry, setEntry, updateEntry

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