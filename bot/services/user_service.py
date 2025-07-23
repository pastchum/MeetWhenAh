from datetime import datetime, timezone

# Import from services
from .database_service import getEntry, setEntry, updateEntry

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
    setEntry("users", user_uuid, {
        "uuid" : user_uuid,
        "tele_id": tele_id,
        "tele_user": username,
        "initialised": True,
        "callout_cleared": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    })

def updateUserInitialised(tele_id: str) -> bool:
    """Update a user's initialised status"""
    updateEntry("users", "tele_id", tele_id, "initialised", True)
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