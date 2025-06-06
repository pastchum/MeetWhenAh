from datetime import datetime
from .database_service import getEntry, setEntry, updateEntry

def updateUsername(user_id: str, username: str) -> bool:
    """Update or create a user's username"""
    user = getEntry("Users", "user_id", user_id)
    
    if user:
        # Update existing user
        user_data = user.copy()
        user_data["username"] = username
        user_data["updated_at"] = datetime.now()
        return updateEntry("Users", user_id, user_data)
    else:
        # Create new user
        user_data = {
            "user_id": user_id,
            "username": username,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        return setEntry("Users", user_id, user_data)

def setUserSleepPreferences(user_id: str, sleep_start: str, sleep_end: str) -> bool:
    """Set a user's sleep preferences"""
    user = getEntry("Users", "user_id", user_id)
    
    if user:
        # Update existing user
        user_data = user.copy()
    else:
        # Create new user
        user_data = {
            "user_id": user_id,
            "created_at": datetime.now()
        }
    
    # Update sleep preferences
    user_data.update({
        "sleep_start": sleep_start,
        "sleep_end": sleep_end,
        "updated_at": datetime.now()
    })
    
    if user:
        return updateEntry("Users", user_id, user_data)
    else:
        return setEntry("Users", user_id, user_data) 