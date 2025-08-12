from datetime import datetime, timezone

# Import from services
from .database_service import getEntry, setEntry, updateEntry, getEntries

# Import from other
import uuid

def getUser(tele_id: str) -> dict:
    """Get a user by their Telegram ID"""
    user = getEntry("users", "tele_id", tele_id)
    return user

def getUserByUuid(uuid: str) -> dict:
    """Get a user by their UUID"""
    user = getEntry("users", "uuid", uuid)
    return user

def setUser(tele_id: str, username: str) -> bool:
    user_uuid = str(uuid.uuid4())
    """Set a user by their Telegram ID"""
    success = setEntry("users", user_uuid, {
        "uuid" : user_uuid,
        "tele_id": tele_id,
        "tele_user": username,
        "initialised": True,
        "callout_cleared": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    })
    return success

def updateUserInitialised(tele_id: str) -> bool:
    """Update a user's initialised status"""
    updateEntry("users", "tele_id", tele_id, "initialised", True)

def updateUserCalloutCleared(tele_id: str) -> bool:
    """
    Update a user's callout cleared status. 
    This means that the user can receive callouts from the bot.
    """
    updateEntry("users", "tele_id", tele_id, "callout_cleared", True)

def updateUsername(tele_id: str, username: str) -> bool:
    """Update or create a user's username"""
    user = getEntry("users", "tele_id", tele_id)
    
    if user:
        # Update existing user
        user_data = user.copy()
        user_data["username"] = username
        user_data["updated_at"] = datetime.now()
        return updateEntry("users", tele_id, user_data)
    else:
        # Create new user
        return setUser(tele_id, username)

def setUserSleepPreferences(tele_id: str, sleep_start: str, sleep_end: str) -> bool:
    """Set a user's sleep preferences"""
    user = getEntry("users", "tele_id", tele_id)
    
    if user:
        # Update existing user
        user_data = user.copy()
    else:
        # Create new user
        user_data = {
            "tele_id": tele_id,
            "created_at": datetime.now()
        }
    
    # Update sleep preferences
    user_data.update({
        "sleep_start": sleep_start,
        "sleep_end": sleep_end,
        "updated_at": datetime.now()
    })
    
    if user:
        return updateEntry("users", tele_id, user_data)
    else:
        return setEntry("users", tele_id, user_data) 
    
def getUpcomingUserEvents(tele_id: str) -> list[dict]:
    """Get a user's upcoming events"""
    #TODO: Add a supabase sql function to get upcoming events for a user based on telegram id
    user = getEntry("users", "tele_id", tele_id)
    if not user:
        return []
    user_uuid = user["uuid"]
    events = getEntries("events", "creator", user_uuid)
    if not events:
        return []
    events = [e for e in events if e["start_date"] > datetime.now(timezone.utc).isoformat()]
    events.sort(key=lambda x: x["start_date"])
    return events