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

def setEntry(table: str, id: str, data: dict) -> bool:
    """Set an entry in a table with the given ID"""
    try:
        response = supabase.table(table).insert(data).execute()
        return True if response.data else False
    except Exception as e:
        print(f"Error setting entry in {table}: {e}")
        return False

def updateEntry(table: str, id: str, data: dict) -> bool:
    """Update an entry in a table with the given ID"""
    try:
        response = supabase.table(table).update(data).eq("event_id", id).execute()
        return True if response.data else False
    except Exception as e:
        print(f"Error updating entry in {table}: {e}")
        return False 