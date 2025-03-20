import firebase_admin
from firebase_admin import firestore
from firebase_admin import credentials
from google.cloud.firestore_v1.base_query import FieldFilter

import json
from datetime import datetime
from icecream import ic


cred = credentials.Certificate("meetwhenbot-firebase-adminsdk-gi7ng-23bb4de9f9.json")
firebase_admin.initialize_app(cred)
db = firestore.client()


def setEntry(col, data): #ref is a file path. data is python dict
    #data = json.dumps(data, indent=2, sort_keys=True, default=str)
    db.collection(col).add(data)

def getEntry(col, field, value, field2=None, value2=None): #col is the collection, whereas field is the data field that fits
    ref = db.collection(col)
    if field2 == None or value2 == None or (field2 == None and value2 == None): #if there is only one set of values to query
        query_ref = ref.where(filter=FieldFilter(field, "==", value))
    else:
        query_ref = ref.where(filter=FieldFilter(field, "==", value)).where(filter=FieldFilter(field2, "==", value2))
 
    for doc in query_ref.stream():
        return doc

def updateEntry(doc, field, value):
    doc.reference.update({
        field: value
    })

def getUserSleepPreferences(user_id):
    """
    Get a user's sleep hours preferences
    
    Args:
        user_id: The telegram user ID
        
    Returns:
        Dict with sleep preferences or None if not set
    """
    user_doc = getEntry("Users", "tele_id", str(user_id))
    if user_doc and "sleep_preferences" in user_doc.to_dict():
        return user_doc.to_dict()["sleep_preferences"]
    return None
    
def setUserSleepPreferences(user_id, sleep_start, sleep_end):
    """
    Set a user's sleep hours preferences
    
    Args:
        user_id: The telegram user ID
        sleep_start: Sleep start time in HHMM format (e.g. "2300" for 11pm)
        sleep_end: Sleep end time in HHMM format (e.g. "0700" for 7am)
    """
    user_doc = getEntry("Users", "tele_id", str(user_id))
    
    sleep_prefs = {
        "start": sleep_start,
        "end": sleep_end
    }
    
    if user_doc:
        updateEntry(user_doc, "sleep_preferences", sleep_prefs)
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
    event_doc = getEntry("Events", "event_id", str(event_id))
    
    if not event_doc:
        return {}
    
    members = event_doc.to_dict().get("members", [])
    
    sleep_preferences = {}
    for user_id in members:
        prefs = getUserSleepPreferences(user_id)
        if prefs:
            sleep_preferences[user_id] = prefs
    
    return sleep_preferences

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