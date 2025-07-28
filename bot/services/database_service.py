import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase: Client = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)

def getEntry(table: str, key_field: str, key_value: str):
    """Get an entry from a table by a key field"""
    try:
        response = supabase.table(table).select("*").eq(key_field, key_value).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None
    except Exception as e:
        print(f"Error getting entry from {table}: {e}")
        return None

def getEntries(table: str, key_field: str, key_value: str):
    """Get multiple entries from a table by a key field"""
    try:
        response = supabase.table(table).select("*").eq(key_field, key_value).execute()
        return response.data
    except Exception as e:
        print(f"Error getting entries from {table}: {e}")
        return None

def setEntry(table: str, id: str, data: dict) -> bool:
    """Set an entry in a table with the given ID"""
    try:
        response = supabase.table(table).insert(data).execute()
        return True if response.data else False
    except Exception as e:
        print(f"Error setting entry in {table}: {e}")
        return False

def setEntries(table: str, data: list[dict]) -> bool:
    """Set multiple entries in a table"""
    try:
        response = supabase.table(table).insert(data).execute()
        return True if response.data else False
    except Exception as e:
        print(f"Error setting entries in {table}: {e}")
        return False

def updateEntry(table: str, id: str, data: dict) -> bool:
    """Update an entry in a table with the given ID"""
    try:
        response = supabase.table(table).update(data).eq("event_id", id).execute()
        return True if response.data else False
    except Exception as e:
        print(f"Error updating entry in {table}: {e}")
        return False 

def deleteEntry(table: str, id_field: str, id: str, key_field: str, key_value: str) -> bool:
    """Delete an entry from a table with the given ID"""
    try:
        response = supabase.table(table).delete().eq(id_field, id).eq(key_field, key_value).execute()
        return True if response.data else False
    except Exception as e:
        print(f"Error deleting entry from {table}: {e}")
        return False
    
def deleteEntries(table: str, id_field: str, id: str, key_field: str, key_values: list[str]) -> bool:
    """Delete multiple entries from a table"""
    try:
        response = supabase.table(table).delete().eq(id_field, id).in_(key_field, key_values).execute()
        return True
    except Exception as e:
        print(f"Error deleting entries from {table}: {e}")
        return False