import os
from urllib.parse import urlencode

def create_web_app_url(path=None, event_id=None, web_app_number=None):
    """
    Create a URL for the Telegram Web App.
    
    Args:
        path (str, optional): The path to append to the base URL (e.g., '/datepicker', '/dragselector').
        event_id (str, optional): The event ID to pass to the web app.
        web_app_number (int, optional): The web app number to use (0 for create, 1 for update).
        
    Returns:
        str: The complete web app URL with query parameters.
    """
    base_url = os.getenv('WEBAPP_URL', 'https://meet-when-ah.vercel.app')
    
    # Add path if provided
    if path:
        if not path.startswith('/'):
            path = '/' + path
        base_url = base_url + path
    
    # Build query parameters
    params = {}
    if web_app_number is not None:
        params['web_app_number'] = web_app_number
    if event_id:
        params['event_id'] = event_id
        
    # Add query string if we have parameters
    if params:
        query_string = urlencode(params)
        return f"{base_url}?{query_string}"
    
    return base_url 