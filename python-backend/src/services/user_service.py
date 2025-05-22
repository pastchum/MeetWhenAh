import os
import supabase
from supabase import create_client, Client, ClientOptions
from pathlib import Path

from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# initialise supabase client
url = str(os.getenv("SUPABASE_URL"))
key = str(os.getenv("SUPABASE_KEY"))
options = ClientOptions(
    auto_refresh_token=True,
    persist_session=True,
    schema="public",
)
supabase_client: Client = create_client(url, key, options=options)

def setEntry(table, data): 
    """Insert a new record into the Supabase table.
    Args:
        table: The table name.
        data: The data to insert (as a dictionary).
    """
    response = supabase_client.from_(table).insert(data).execute()
    return response

def getEntry(table, field, value, field2=None, value2=None): 
    """Get a record from the Supabase table based on a field and value.
    Args:
        table: The table name.
        field: The field to filter by.
        value: The value to filter by.
        field2: An optional second field to filter by.
        value2: An optional second value to filter by.
    Returns:
        The first matching record in a dictionary or None if not found.
    """
    if field2 and value2:
        response = supabase_client.from_(table).select("*").eq(field, value).eq(field2, value2).execute()
    else:
        response = supabase_client.from_(table).select("*").eq(field, value).execute()

    if response.status_code == 200:
        data = response.data
        if data:
            return data[0]
        else:
            return None

def updateEntry(table, id_field, id_value, field, value):
    """
    Update a specific field in a record in the Supabase table.

    Args:
        table: The table name.
        id_field: The field used to identify the record (e.g., primary key).
        id_value: The value of the identifier field.
        field: The field to update.
        value: The new value to set for the field.
    Returns:
        The response from the Supabase API.
    """
    response = supabase_client.from_(table).update({field: value}).eq(id_field, id_value).execute()
    return response

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
        user_data = getEntry("Users", "tele_id", str(tele_id))
        if user_data:
            updateEntry("Users", "tele_id", user_data["tele_id"], "tele_user", new_username)
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
        tuple: A tuple of (sleep_start, sleep_end), or (None, None) if not found.
    """
    try:
        user_data = getEntry("Users", "tele_id", str(tele_id))
        if user_data and "sleep_preferences" in user_data:
            return user_data["sleep_preferences"]
        return None, None
    except Exception as e:
        print(f"Error getting sleep preferences: {e}")
        return None, None

def setSleepPreferences(tele_id, sleep_start, sleep_end):
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
        user_data = getEntry("Users", "tele_id", str(tele_id))
        
        sleep_prefs = {
            "start": sleep_start,
            "end": sleep_end
        }
        
        if user_data:
            updateEntry("Users", "tele_id", user_data["tele_id"], "sleep_preferences", sleep_prefs)
        else:
            # Create new user record if it doesn't exist
            setEntry("Users", {
                "tele_id": str(tele_id),
                "initialised": True,
                "callout_cleared": True,
                "sleep_preferences": sleep_prefs
            })
        return True
    except Exception as e:
        print(f"Error setting sleep preferences: {e}")
        return False 