#import firebase_admin
#from firebase_admin import firestore
#from firebase_admin import credentials
#from google.cloud.firestore_v1.base_query import FieldFilter

import os
from supabase import create_client, Client, ClientOptions

import json
from datetime import datetime
from icecream import ic

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


#cred = credentials.Certificate("meetwhenbot-firebase-adminsdk-gi7ng-23bb4de9f9.json")
#firebase_admin.initialize_app(cred)
#db = firestore.client()
url = str(os.getenv("SUPABASE_URL"))
key = str(os.getenv("SUPABASE_KEY"))
options = ClientOptions(
    auto_refresh_token=True,
    persist_session=True,
    schema="public",
)
supabase_client: Client = create_client(url, key, options=options)


def setEntry(table, data): #ref is a file path. data is python dict
    #data = json.dumps(data, indent=2, sort_keys=True, default=str)
    #db.collection(col).add(data)
    """Insert a new record into the Supabase table.
    Args:
        table: The table name.
        data: The data to insert (as a dictionary).
    """
    response = supabase_client.from_(table).insert(data).execute()
    if response.status_code == 201:
        ic(f"Data inserted successfully into {table}")
    else:
        ic(f"Error inserting data into {table}: {response.status_code} - {response.data}")
    return response

def getEntry(table, field, value, field2=None, value2=None): #col is the collection, whereas field is the data field that fits
    #ref = db.collection(col)
    #if field2 == None or value2 == None or (field2 == None and value2 == None): #if there is only one set of values to query
    #    query_ref = ref.where(filter=FieldFilter(field, "==", value))
    #else:
    #    query_ref = ref.where(filter=FieldFilter(field, "==", value)).where(filter=FieldFilter(field2, "==", value2))
 
    #for doc in query_ref.stream():
    #    return doc
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
        response = supabase_client.from_(table).select("*").eq(field, value).eq(field2, value2)
    else:
        response = supabase_client.from_(table).select("*").eq(field, value)

    if response.status_code == 200:
        data = response.data
        if data:
            return data[0]
        else:
            ic(f"No data found for {field} = {value} in {table}")
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
    if response.status_code == 200:
        ic(f"Field '{field}' updated successfully in {table} where {id_field} = {id_value}")
    else:
        ic(f"Error updating field '{field}' in {table}: {response.status_code} - {response.data}")
    return response

def getUserSleepPreferences(user_id):
    """
    Get a user's sleep hours preferences
    
    Args:
        user_id: The telegram user ID
        
    Returns:
        Dict with sleep preferences or None if not set
    """
    user_data = getEntry("Users", "tele_id", str(user_id))
    if user_data and "sleep_preferences" in user_data:
        return user_data["sleep_preferences"]
    return None
    
def setUserSleepPreferences(user_id, sleep_start, sleep_end):
    """
    Set a user's sleep hours preferences
    
    Args:
        user_id: The telegram user ID
        sleep_start: Sleep start time in HHMM format (e.g. "2300" for 11pm)
        sleep_end: Sleep end time in HHMM format (e.g. "0700" for 7am)
    """
    user_data = getEntry("Users", "tele_id", str(user_id))
    
    sleep_prefs = {
        "start": sleep_start,
        "end": sleep_end
    }
    
    if user_data:
        updateEntry("Users", "tele_id", user_data["tele_id"], "sleep_preferences", sleep_prefs)
    else:
        # Create new user record if it doesn't exist
        setEntry("Users", {
            "tele_id": str(user_id),
            "initialised": True,
            "callout_cleared": True,
            "sleep_preferences": sleep_prefs
        })

def getEventSleepPreferences(event_id):
    """
    Get sleep preferences for all users in an event
    
    Args:
        event_id: The event ID
        
    Returns:
        Dict mapping user IDs to their sleep preferences
    """
    event_data = getEntry("Events", "event_id", str(event_id))
    
    if not event_data:
        return {}
    
    members = event_data.get("members", [])
    if not members:
        return {}
    
    sleep_preferences = {}
    for user_id in members:
        prefs = getUserSleepPreferences(user_id)
        if prefs:
            sleep_preferences[user_id] = prefs
    
    return sleep_preferences

def getUserByUsername(username):
    """
    Get a user by their Telegram username
    
    Args:
        username: The Telegram username (without the @ symbol)
        
    Returns:
        The user document or None if not found
    """
    username = username.lstrip('@')  # Remove @ if it exists
    
    response = supabase_client.from_("Users").select("*").eq("tele_user", username).execute()
    if response.status_code == 200:
        data = response.data
        if data:
            return data[0]
        else:
            ic(f"No user found with username {username}")
            return None
    else:
        ic(f"Error fetching user by username: {response.status_code} - {response.data}")
    return None

def updateUsername(user_id, new_username):
    """
    Update a user's Telegram username
    
    Args:
        user_id: The telegram user ID
        new_username: The new username
        
    Returns:
        True if successful, False otherwise
    """
    user_data = getEntry("Users", "tele_id", str(user_id))
    
    if user_data:
        updateEntry("Users", "tele_id", user_data["tele_id"], "tele_user", new_username)
        
        # Also update any references in previous availability
        # This ensures consistency when username changes
        
        if "previous_usernames" not in user_data:
            updateEntry("Users", "tele_id", user_data["tele_id"], "previous_usernames", [user_data.get("tele_user", "")])
            
        return True
    
    return False

def updateUserAvailability(username, event_id, availability_data):
    """
    Update a user's availability for an event
    
    Args:
        username: The user's Telegram username
        event_id: The event ID
        availability_data: List of availability data objects with date and time info
        
    Returns:
        True if successful, False otherwise
    """
    user_data = getUserByUsername(username)
    
    if not user_data:
        ic(f"User with username {username} not found")
        return False
    
    user_id = user_data.get("tele_id")
    
    event_data = getEntry("Events", "event_id", str(event_id))
    
    if not event_data:
        ic(f"Event with ID {event_id} not found")
        return False
    
    # Get current availability data
    hours_available = event_data.get("hours_available", [])
    event_type = event_data.get("event_type", "general")
    
    # Remove this user's previous selections
    for day in hours_available:
        for time_slot, users in day.items():
            if time_slot != "date" and isinstance(users, list):
                if user_id in users:
                    users.remove(user_id)
    
    # Add new selections
    for day_data in availability_data:
        date_str = day_data.get("date")
        time_slot = day_data.get("time")
        
        # Find the right day in hours_available
        for day in hours_available:
            if hasattr(day["date"], "date"):
                day_date = day["date"].date()
            else:
                day_date = day["date"]
                
            # Convert incoming date format (could be DD/MM/YYYY)
            if "/" in date_str:
                try:
                    date_obj = datetime.strptime(date_str, "%d/%m/%Y").date()
                except ValueError:
                    try:
                        date_obj = datetime.strptime(date_str, "%m/%d/%Y").date()
                    except ValueError:
                        ic(f"Could not parse date {date_str}")
                        continue
            else:
                try:
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
                except ValueError:
                    ic(f"Could not parse date {date_str}")
                    continue
            
            # Check if this is the right day
            if day_date == date_obj:
                if time_slot in day:
                    # Add user to this time slot
                    if user_id not in day[time_slot]:
                        day[time_slot].append(user_id)
                else:
                    ic(f"Time slot {time_slot} not found in day {day_date}")
                    
    # Update the event
    updateEntry("Events", "event_id", event_id, "hours_available", hours_available)
    
    # Also save this availability pattern to user's profile for this event type
    
    # Initialize availability_patterns if it doesn't exist
    if "availability_patterns" not in user_data:
        user_data["availability_patterns"] = {}
    
    # Initialize this event type if it doesn't exist
    if event_type not in user_data["availability_patterns"]:
        user_data["availability_patterns"][event_type] = {}
    
    # Save patterns by day of week
    for day_data in availability_data:
        try:
            if "/" in day_data["date"]:
                day_date = datetime.strptime(day_data["date"], "%d/%m/%Y")
            else:
                day_date = datetime.strptime(day_data["date"], "%Y-%m-%d")
                
            day_of_week = day_date.strftime("%A")  # Monday, Tuesday, etc.
            
            # Save time slot for this day of week
            if day_of_week not in user_data["availability_patterns"][event_type]:
                user_data["availability_patterns"][event_type][day_of_week] = []
            
            user_data["availability_patterns"][event_type][day_of_week].append(day_data["time"])
        except Exception as e:
            ic(f"Error processing day data: {e}")
    
    # Update user profile
    updateEntry("Users", "tele_id", user_data["tele_id"], "availability_patterns", user_data["availability_patterns"])
    
    return True

def getUserAvailability(username, event_id):
    """
    Get a user's availability for an event
    
    Args:
        username: The user's Telegram username
        event_id: The event ID
        
    Returns:
        List of availability data or None if not found
    """
    user_data = getUserByUsername(username)
    
    if not user_data:
        ic(f"User with username {username} not found")
        return None
    
    user_id = user_data.get("tele_id")
    
    event_data = getEntry("Events", "event_id", str(event_id))
    
    if not event_data:
        ic(f"Event with ID {event_id} not found")
        return None
    
    # Get current availability data
    hours_available = event_data.get("hours_available", [])
    
    # Extract this user's availability
    user_availability = []
    
    for day in hours_available:
        if hasattr(day["date"], "date"):
            date_str = day["date"].date().strftime("%Y-%m-%d")
        else:
            date_str = day["date"].strftime("%Y-%m-%d")
            
        for time_slot, users in day.items():
            if time_slot != "date" and isinstance(users, list):
                if user_id in users:
                    user_availability.append({
                        "date": date_str,
                        "time": time_slot
                    })
    
    return user_availability

"""
data = {
    "group_id" : "21039",
    "members" : ["123123", "51248124", "4124124"],
    "dates_chosen" : [datetime.now(), datetime.now()],
    "event_name" : "test_event",
    "hours occupied": { str(i): [] for i in range(25) },
    "timeout": datetime.now()
    "inline_message_id" : "123123"
}
"""