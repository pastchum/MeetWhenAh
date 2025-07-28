from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

# Import from scheduler
from scheduler.scheduler import Scheduler

# Import from services
from .database_service import getEntry, setEntry, updateEntry, getEntries, deleteEntries, setEntries, deleteEntry
from .user_service import getUser

# Import from utils
from utils.date_utils import format_date_for_message, format_time_from_iso, parse_date, parse_time, format_time

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
        "start_date": start_date,
        "end_date": end_date,
        "start_hour": start_hour,
        "end_hour": end_hour,
        "creator": creator_uuid,
    }
    print(event_data)
    success = setEntry("events", event_id, event_data)
    print(success)
    return event_id if success else None

def join_event_by_uuid(event_id: str, user_uuid: str) -> bool:
    """Add a user to an event's participants"""
    event = getConfirmedEvent(event_id)
    if not event:
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

def join_event(event_id: str, tele_id: str) -> bool:
    """Add a user to an event's participants"""
    event = getConfirmedEvent(event_id)
    if not event:
        return False
    user = getUser(tele_id)
    if not user:
        return False
    user_uuid = user["uuid"]
    
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

def leave_event(event_id: str, tele_id: str) -> bool:
    """Remove a user from an event's participants"""
    event = getConfirmedEvent(event_id)
    if not event:
        return False
    user = getUser(tele_id)
    if not user:
        return False
    user_uuid = user["uuid"]
    success = deleteEntry("membership", "event_id", event_id, "user_uuid", user_uuid)
    if not success:
        return False
    return True

def set_chat(event_id: str, chat_id: int, thread_id: int = None) -> bool:
    """Set a chat for an event"""
    print("Setting chat for event", event_id, chat_id, thread_id)
    event = getEvent(event_id)
    if not event:
        print("Event not found")
        return False
    chat_data = {
        "event_id": event_id,
        "chat_id": chat_id,
        "thread_id": thread_id,
        "is_reminders_enabled": False
    }
    success = setEntry("event_chats", event_id, chat_data)
    if not success:
        return False
    return True

def get_event_chat(event_id: str) -> Tuple[int, int]:
    """Get a chat for an event"""
    event_chat = getEntry("event_chats", "event_id", event_id)
    print("event_chat", event_chat)
    if not event_chat:
        return None, None
    return event_chat["chat_id"], event_chat["thread_id"]

def check_ownership(event_id: str, tele_id: str) -> bool:
    """Check if a user is the owner of an event"""
    event = getEvent(event_id)
    if not event:
        return False
    creator_uuid = event["creator"]
    user = getUser(tele_id)
    if not user:
        return False
    user_uuid = user["uuid"]
    return creator_uuid == user_uuid

def check_membership(event_id: str, tele_id: str) -> bool:
    """Check if a user is a member of an event"""
    event = getConfirmedEvent(event_id)
    if not event:
        return False
    user = getUser(tele_id)
    if not user:
        return False
    user_uuid = user["uuid"]
    membership = getEntries("membership", "event_id", event_id)
    for member in membership:
        if member["user_uuid"] == user_uuid:
            return True
    return False

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

def get_event_availability(event_id: str) -> List[Dict]:
    """Get all availability blocks for an event"""
    availability = getEntries("availability_blocks", "event_id", event_id)
    return availability

def getUserAvailability(tele_id: str, event_id: str) -> List[Dict]:
    """Get a user's availability for an event"""
    availability = get_event_availability(event_id)
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
    
def get_event_best_time(event_id: str) -> List[Dict]:
    """Get the best time for an event"""

    # get event data
    event = getEntry("events", "event_id", event_id)
    if not event:
        return []
    
    min_participants = event.get("min_participants", 2)
    min_duration_blocks = event.get("min_duration", 2)
    max_duration_blocks = event.get("max_duration", 4)

    scheduler = Scheduler(min_participants=min_participants, min_block_size=min_duration_blocks, max_block_size=max_duration_blocks)

    availability_blocks = get_event_availability(event_id)
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

def generate_confirmed_event_description(event_id: str) -> str:
    """Generate a description for a confirmed event"""
    event_data = getEvent(event_id)
    confirmed_event_data = getConfirmedEvent(event_id)
    if not confirmed_event_data:
        return "Event not confirmed"
    description = ""
    if not event_data:
        return description
    # add event name and description
    description += f"Event Name: {event_data['event_name']}\n"
    description += f"Event Description: {event_data['event_description']}\n"

    # parse start time
    start_date = parse_date(confirmed_event_data['confirmed_start_time'])
    start_date_str = format_date_for_message(start_date)
    start_time_str = format_time_from_iso(confirmed_event_data['confirmed_start_time'])

    # parse end time
    end_date = parse_date(confirmed_event_data['confirmed_end_time'])
    end_date_str = format_date_for_message(end_date)
    end_time_str = format_time_from_iso(confirmed_event_data['confirmed_end_time'])

    # add start and end time
    description += f"Start Date: {start_date_str} {start_time_str} to End Date: {end_date_str} {end_time_str}\n"

    return description

def generate_confirmed_event_participants_list(event: dict) -> str:
    """Generate a list for the participants of a confirmed event"""
    description = ""
    event_id = event["event_id"]
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
        start_date = parse_date(event['start_date'])
        start_date_str = format_date_for_message(start_date)
        description += f"Start Date: {start_date_str}\n"
    if "end_date" in event: 
        end_date = parse_date(event['end_date'])
        end_date_str = format_date_for_message(end_date)
        description += f"End Date: {end_date_str}\n"
    if "start_hour" in event and "end_hour" in event:
        start_hour = format_time(parse_time(event['start_hour']))
        end_hour = format_time(parse_time(event['end_hour']))
        description += f"Start Time: {start_hour} to End Time: {end_hour}\n"
    return description

if __name__ == "__main__":
    event_id = "44e211d3-a094-4133-9ea0-4539c091c07c"
    event = getEntry("events", "event_id", event_id)
    print(event)

    best_time = get_event_best_time(event_id)
    print(best_time)
