import os
from urllib.parse import urlencode

def create_web_app_url(event_id=None, web_app_number=1):
    """
    Create a URL for the Telegram Web App.
    
    Args:
        event_id (str, optional): The event ID to pass to the web app.
        web_app_number (int, optional): The web app number to use (0 for create, 1 for update).
        
    Returns:
        str: The complete web app URL with query parameters.
    """
    base_url = os.getenv('WEBAPP_URL', 'https://meetwhenah.vercel.app')
    
    params = {
        'web_app_number': web_app_number
    }
    
    if event_id:
        params['event_id'] = event_id
        
    query_string = urlencode(params)
    return f"{base_url}?{query_string}" 