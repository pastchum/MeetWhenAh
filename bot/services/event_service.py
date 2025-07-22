from datetime import datetime, timezone
from typing import Dict, List, Optional

# Import from scheduler
from scheduler.scheduler import Scheduler

# Import from services
from .database_service import getEntry, setEntry, updateEntry, getEntries, deleteEntries, setEntries

# Import from other
import uuid

def getEvent(event_id: str) -> Optional[Dict]:
    """Get event details by ID"""
    event = getEntry("events", "event_id", event_id)
    return event if event else None


def create_event(event_name: str, event_description: str, start_date: str, end_date: str, creator_id: str, auto_join: bool = True, event_type: str = "general", start_hour: str = "00:00:00.000000+08:00", end_hour: str = "23:30:00.000000+08:00") -> str:
    """Create a new event and return its ID"""
    event_id = str(uuid.uuid4())
    creator_details = getEntry("users", "tele_id", creator_id)
    creator_uuid = creator_details["uuid"]
    event_data = {
        "event_id": event_id,
        "event_name": event_name,
        "event_description": event_description,
        "event_type": event_type,
        "start_date": datetime.strptime(start_date, "%Y-%m-%d").replace(tzinfo=timezone.utc).isoformat(),
        "end_date": datetime.strptime(end_date, "%Y-%m-%d").replace(tzinfo=timezone.utc).isoformat(),
        "start_hour": start_hour,
        "end_hour": end_hour,
        "creator": creator_uuid,
    }
    print(event_data)
    success = setEntry("events", event_id, event_data)
    print(success)
    return event_id if success else None

def get_event_by_id(event_id: str) -> Dict:
    """Get event details by ID"""
    event = getEntry("events", "event_id", event_id)
    return event.to_dict() if event else None

def join_event(event_id: str, user_uuid: str) -> bool:
    """Add a user to an event's participants"""
    event = getEntry("event_confirmations", "event_id", event_id)
    if not event:
        return False
    user_data = getEntry("users", "uuid", user_uuid)
    if not user_data:
        return False
    
    # add user to event membership table
    membership_data = {
        "event_id": event_id,
        "user_uuid": user_uuid,
        "joined_at": datetime.now(timezone.utc).isoformat(),
        "emoji_icon": "👋"
    }
    success = setEntry("membership", event_id, membership_data)
    if not success:
        return False
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

def getUserAvailability(tele_id: str, event_id: str) -> List[Dict]:
    """Get a user's availability for an event"""
    availability = getEntries("availability_blocks", "event_id", event_id)
    if not availability:
        return []
    
    user_data = getEntry("users", "tele_id", tele_id)
    if not user_data:
        return []
    user_uuid = user_data["uuid"]
    if not user_uuid:
        return []
        
    user_availability = [x for x in availability if x["user_uuid"] == user_uuid]
    return user_availability

def updateUserAvailability(tele_id: str, event_id: str, availability_data: List[Dict]) -> bool:
    """Update a user's availability for an event"""
    user_data = getEntry("users", "tele_id", tele_id)
    if not user_data:
        return False
    
    user_uuid = user_data["uuid"]
    if not user_uuid:
        return False

    # delete all availability blocks for the user for the event previously, if any
    successful_delete = deleteEntries("availability_blocks", "event_id", event_id, "user_uuid", [user_uuid])
    if not successful_delete:
        return False

    if not availability_data: # no need to set if no availability data
        return True
    successful_set = setEntries("availability_blocks", availability_data)
    if not successful_set:
        return False
    return True
    
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
    
def get_event_best_time(event_id: str) -> List[Dict]:
    """Get the best time for an event"""
    scheduler = Scheduler()

    availability_blocks = getEntries("availability_blocks", "event_id", event_id)
    if not availability_blocks:
        return []
    
    best_event_blocks = scheduler._process_availability_blocks(availability_blocks)

    return best_event_blocks

def confirmEvent(event_id: str, best_start_time: str, best_end_time: str) -> bool:
    """Confirm an event"""
    event = getEntry("events", "event_id", event_id)
    if not event:
        return False
    # set event to confirmed
    #updateEntry("events", event_id, {"confirmed": True})

    # set event confirmation data
    confirmed_event_data = {
        "event_id": event_id,
        "confirmed_at": datetime.now(timezone.utc).isoformat(),
        "confirmed_start_time": best_start_time,
        "confirmed_end_time": best_end_time
    }
    success = setEntry("event_confirmations", event_id, confirmed_event_data)
    if not success:
        return False
    return True

def getConfirmedEvent(event_id: str) -> Dict:
    """Get a confirmed event"""
    event = getEntry("event_confirmations", "event_id", event_id)
    return event if event else None

def generate_confirmed_event_description(event: dict) -> str:
    """Generate a description for a confirmed event"""
    description = ""
    event_id = event[event_id]
    event_data = getEntry("_datas", "_data_id", event_id)
    if not event_data:
        return description
    description += f"Event Name: {event_data['event_name']}\n"
    description += f"Event Description: {event_data['event_description']}\n"
    description += f"Start Time: {event['confirmed_start_time']}\n"
    description += f"End Time: {event['confirmed_end_time']}\n"

    return description

def generate_confirmed_event_participants_list(event: dict) -> str:
    """Generate a list for the participants of a confirmed event"""
    description = ""
    event_id = event[event_id]
    participants = getEntries("membership", "event_id", event_id)
    if not participants:
        return description
    description = ""
    for participant in participants:
        user_data = getEntry("users", "uuid", participant["user_uuid"])
        if user_data:
            description += f"{user_data['tele_user']}\n"
    return description

def generate_event_description(event: dict) -> str:
    """Generate a description for an event"""
    description = ""
    if not event:
        return description
    if "event_name" in event:
        description += f"Event Name: {event['event_name']}\n"
    if "event_description" in event:
        description += f"Event Description: {event['event_description']}\n"
    if "start_date" in event:
        start_date = datetime.strptime(event['start_date'][:10], "%Y-%m-%d").strftime("%d %B %Y")
        description += f"Start Date: {start_date}\n"
    if "end_date" in event: 
        end_date = datetime.strptime(event['end_date'][:10], "%Y-%m-%d").strftime("%d %B %Y")
        description += f"End Date: {end_date}\n"
    if "start_hour" in event and "end_hour" in event:
        start_hour = datetime.strptime(event['start_hour'][:8], "%H:%M:%S").strftime("%H:%M")
        end_hour = datetime.strptime(event['end_hour'][:8], "%H:%M:%S").strftime("%H:%M")
        description += f"Start Time: {start_hour} to End Time: {end_hour}\n"
    return description


if __name__ == "__main__":
    event_id = "44e211d3-a094-4133-9ea0-4539c091c07c"
    event = getEntry("events", "event_id", event_id)
    print(event)

    best_time = get_event_best_time(event_id)
    print(best_time)
