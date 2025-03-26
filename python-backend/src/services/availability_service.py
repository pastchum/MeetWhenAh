from .user_service import getEntry, setEntry, updateEntry
from .event_service import getUserAvailability as getEventUserAvailability

def getUserAvailability(username, event_id):
    """
    Get a user's availability for an event.
    
    Args:
        username (str): The username.
        event_id (str): The event ID.
        
    Returns:
        dict: The user's availability data.
    """
    return getEventUserAvailability(username, event_id)

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
        user_doc = getEntry("Users", "tele_id", str(tele_id))
        if user_doc:
            doc_id = user_doc.id
            updateEntry("Users", doc_id, {
                "sleep_start": sleep_start,
                "sleep_end": sleep_end,
                "temp_sleep_start": None  # Clear temporary storage
            })
            return True
            
        setEntry("Users", {
            "tele_id": str(tele_id),
            "sleep_start": sleep_start,
            "sleep_end": sleep_end
        })
        return True
    except Exception as e:
        print(f"Error setting sleep preferences: {e}")
        return False 