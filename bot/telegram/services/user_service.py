from datetime import datetime
from .database_service import getEntry, setEntry, updateEntry
import uuid

def getUser(tele_id: str) -> dict:
    """Get a user by their Telegram ID"""
    user = getEntry("Users", "tele_id", tele_id)
    return user

def setUser(tele_id: str, username: str) -> bool:
    """Set a user by their Telegram ID"""
    setEntry("users", {
        "uuid" : str(uuid.uuid4()),
        "tele_id": tele_id,
        "tele_user": username,
        "initialised": True,
        "callout_cleared": True,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
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