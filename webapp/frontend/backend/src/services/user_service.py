from pathlib import Path

from datetime import datetime

from .database_service import getEntry, setEntry, updateEntry

def updateUsername(tele_id, new_username):
    """
    Update a user's username.
    
    Args:
        tele_id (int): The user's Telegram ID.
        new_username (str): The new username.
        
    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        user_data = getEntry("users", "tele_id", str(tele_id))
        if user_data:
            updateEntry("users", "tele_id", tele_id, "tele_user", new_username)
            return True
        return False
    except Exception as e:
        print(f"Error updating username: {e}")
        return False

def getUserSleepPreferences(tele_id):
    """
    Get a user's sleep preferences.
    
    Args:
        tele_id (int): The user's Telegram ID.
        
    Returns:
        tuple: A tuple of (sleep_start_time, sleep_end_time), or (None, None) if not found.
    """
    try:
        user_data = getEntry("users", "tele_id", str(tele_id))
        if user_data and "sleep_start_time" and "sleep_end_time" in user_data:
            return user_data["sleep_start_time"], user_data["sleep_end_time"]
        return None, None
    except Exception as e:
        print(f"Error getting sleep preferences: {e}")
        return None, None

def setUserSleepPreferences(tele_id, sleep_start, sleep_end):
    """
    Set a user's sleep preferences.
    
    Args:
        tele_id (int): The user's Telegram ID.
        sleep_start (str): Sleep start time in HHMM format.
        sleep_end (str): Sleep end time in HHMM format.
        
    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        user_data = getEntry("users", "tele_id", str(tele_id))
        
        if user_data:
            updateEntry("users", "tele_id", tele_id, "sleep_start_time", sleep_start)
            updateEntry("users", "tele_id", tele_id, "sleep_end_time", sleep_end)
            updateEntry("users", "tele_user", tele_id, "tmp_sleep_start", None)
        else:
            # Create new user record if it doesn't exist
            setEntry("users", {
                "tele_id": str(tele_id),
                "sleep_start_time": sleep_start,
                "sleep_end_time": sleep_end
            })
        return True
    except Exception as e:
        print(f"Error setting sleep preferences: {e}")
        return False 
    