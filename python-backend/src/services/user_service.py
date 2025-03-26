import os
from google.cloud import firestore
import firebase_admin
from firebase_admin import credentials
from pathlib import Path

# Get the path to the service account file
service_account_path = Path(__file__).parent.parent.parent / 'meetwhenbot-firebase-adminsdk-gi7ng-23bb4de9f9.json'

# Initialize Firebase Admin SDK if not already initialized
if not firebase_admin._apps:
    cred = credentials.Certificate(str(service_account_path))
    firebase_admin.initialize_app(cred)

# Initialize Firestore client
db = firestore.Client.from_service_account_json(str(service_account_path))

def getEntry(collection, field, value):
    """
    Get a document from a collection where field matches value.
    
    Args:
        collection (str): The collection name.
        field (str): The field to match.
        value: The value to match.
        
    Returns:
        DocumentSnapshot: The matching document, or None if not found.
    """
    docs = db.collection(collection).where(field, '==', value).limit(1).stream()
    return next(docs, None)

def setEntry(collection, data):
    """
    Set a document in a collection.
    
    Args:
        collection (str): The collection name.
        data (dict): The document data.
        
    Returns:
        DocumentReference: The reference to the created document.
    """
    return db.collection(collection).document().set(data)

def updateEntry(collection, doc_id, data):
    """
    Update a document in a collection.
    
    Args:
        collection (str): The collection name.
        doc_id (str): The document ID.
        data (dict): The update data.
        
    Returns:
        DocumentReference: The reference to the updated document.
    """
    return db.collection(collection).document(doc_id).update(data)

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
        user_doc = getEntry("Users", "tele_id", str(tele_id))
        if user_doc:
            doc_id = user_doc.id
            updateEntry("Users", doc_id, {"tele_user": new_username})
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
        user_doc = getEntry("Users", "tele_id", str(tele_id))
        if user_doc:
            user_data = user_doc.to_dict()
            return user_data.get("sleep_start"), user_data.get("sleep_end")
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
        user_doc = getEntry("Users", "tele_id", str(tele_id))
        if user_doc:
            doc_id = user_doc.id
            updateEntry("Users", doc_id, {
                "sleep_start": sleep_start,
                "sleep_end": sleep_end
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