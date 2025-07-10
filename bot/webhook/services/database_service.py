import os
import supabase
from supabase import create_client, Client, ClientOptions

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
    try:
        if field2 and value2:
            response = supabase_client.from_(table).select("*").eq(field, value).eq(field2, value2).execute()
        else:
            response = supabase_client.from_(table).select("*").eq(field, value).execute()

        data = response.data
        if data:
            return data[0]  # Return the first matching record
        else:
            return None
    except Exception as e:
        print(f"Exception in getEntry: {e}")
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