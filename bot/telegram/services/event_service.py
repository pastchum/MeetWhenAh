from datetime import datetime, timezone
from typing import Dict, List, Optional
from .database_service import getEntry, setEntry, updateEntry
import uuid

def getEvent(event_id: str) -> Optional[Dict]:
    """Get event details by ID"""
    event = getEntry("events", "event_id", event_id)
    return event if event else None


def create_event(event_name: str, event_description: str, start_date: str, end_date: str, creator_id: str, auto_join: bool = True, event_type: str = "general", start_hour: str = "00:00:00.000000+08:00", end_hour: str = "23:30:00.000000+08:00") -> str:
    """Create a new event and return its ID"""
    event_id = str(uuid.uuid4())
    event_data = {
        "event_id": event_id,
        "event_name": event_name,
        "event_description": event_description,
        "event_type": event_type,
        "start_date": datetime.strptime(start_date, "%Y-%m-%d").replace(tzinfo=timezone.utc),
        "end_date": datetime.strptime(end_date, "%Y-%m-%d").replace(tzinfo=timezone.utc),
        "start_hour": start_hour,
        "end_hour": end_hour,
        "creator": creator_id,
        "created_at": datetime.now()
    }
    print(event_data)
    success = setEntry("events", event_id, event_data)
    print(success)
    return event_id if success else None

def get_event_by_id(event_id: str) -> Dict:
    """Get event details by ID"""
    event = getEntry("events", "event_id", event_id)
    return event.to_dict() if event else None

def join_event(event_id: str, user_id: str) -> bool:
    """Add a user to an event's participants"""
    event = getEntry("events", "event_id", event_id)
    if not event:
        return False
        
    event_data = event.to_dict()
    if user_id not in event_data.get("participants", []):
        event_data["participants"] = event_data.get("participants", []) + [user_id]
        return updateEntry("events", event_id, event_data)
    return True

def getEventSleepPreferences(event_id: str) -> Dict[str, Dict[str, int]]:
    """Get sleep preferences for all participants in an event"""
    event = getEntry("events", "event_id", event_id)
    if not event:
        return {}
    
    sleep_prefs = {}
    for user_id in event.get("participants", []):
        user = getEntry("users", "uuid", user_id)
        if user and "sleep_start" in user and "sleep_end" in user:
            sleep_prefs[user_id] = {
                "start": user["sleep_start"],
                "end": user["sleep_end"]
            }
    
    return sleep_prefs

def getUserAvailability(username: str, event_id: str) -> List[Dict]:
    """Get a user's availability for an event"""
    availability = getEntry("availability", "event_id", event_id)
    if not availability:
        return []
    
    user_availability = availability.get(username, [])
    return user_availability

def updateUserAvailability(username: str, event_id: str, availability_data: List[Dict]) -> bool:
    """Update a user's availability for an event"""
    availability = getEntry("availability", "event_id", event_id)
    
    if availability:
        # Update existing availability
        availability_data = availability.copy()
        availability_data[username] = availability_data
        availability_data["updated_at"] = datetime.now()
        return updateEntry("availability", event_id, availability_data)
    else:
        # Create new availability
        availability_data = {
            "event_id": event_id,
            username: availability_data,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        return setEntry("availability", event_id, availability_data) 

def getUserEvents(user_id):
    """Get all events that a user is a member of."""
    try:
        events = []
        from ..services.user_service import supabase_client
        
        # Query events where user is a member
        event_data = supabase_client.from_('events').select('*').filter('members', 'cs', str(user_id)).execute()
        
        for event_data in event_data['data']:
            events.append({
                'id': event_data.get('event_id'),
                'name': event_data.get('event_name', 'Unnamed Event')
            })
            
        return events
    except Exception as e:
        print(f"Error getting user events: {e}")
        return [] 