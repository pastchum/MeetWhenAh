import os
from urllib.parse import urlencode

def create_web_app_url(path: str, web_app_number: int = 1, **params) -> str:
    """
    Create a URL for the web app with the given path and parameters.
    
    Args:
        path (str): The path to the web app page (e.g., '/dragselector')
        web_app_number (int): The web app number for different functionalities
        **params: Additional query parameters to add to the URL
    
    Returns:
        str: The complete web app URL
    """
    # Get the base URL from environment variable or use default
    base_url = os.getenv('WEBAPP_URL', 'https://meet-when-ah.vercel.app')
    
    # Remove leading slash if present to avoid double slashes
    if path.startswith('/'):
        path = path[1:]
    
    # Add web_app_number to params
    params['web_app_number'] = web_app_number
    
    # Build the query string
    query_string = urlencode(params)
    
    # Combine all parts
    url = f"{base_url}/{path}"
    if query_string:
        url = f"{url}?{query_string}"
    
    return url 