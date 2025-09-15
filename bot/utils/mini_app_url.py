import os
from urllib.parse import urlencode

def get_mini_app_url(action: str, **params) -> str:
    """
    Generate Mini App URL based on environment
    - development: Uses local HTTPS webapp or production webapp
    - staging: Uses production webapp
    - production: Uses production webapp
    """
    environment = os.getenv('ENVIRONMENT', 'development')
    bot_username = os.getenv('BOT_USERNAME')
    
    if not bot_username:
        raise ValueError(f"BOT_USERNAME not set for environment: {environment}")
    
    # For local development with HTTPS
    if environment == 'development' and os.getenv('USE_LOCAL_WEBAPP') == 'true':
        localhost_port = os.getenv('LOCALHOST_PORT', '3000')
        webapp_url = f'https://localhost:{localhost_port}'
    elif environment == 'staging':
        webapp_url = 'https://meet-when-ah-git-staging.vercel.app'
    else:
        webapp_url = 'https://meet-when-ah.vercel.app'
    
    # Build the parameter string
    if params:
        # For single parameter, use the value directly (no URL encoding to match original behavior)
        if len(params) == 1:
            param_name, param_value = next(iter(params.items()))
            startapp_param = f"{action}={param_value}"
        else:
            # For multiple parameters, use urlencode but replace = with %3D and & with %26
            params_str = urlencode(params)
            encoded_params_str = params_str.replace('=', '%3D').replace('&', '%26')
            startapp_param = f"{action}={encoded_params_str}"
    else:
        startapp_param = action
    
    return f"https://t.me/{bot_username}/meetwhenah?startapp={startapp_param}"

def get_webapp_url(path: str, **params) -> str:
    """Generate direct webapp URL for local testing"""
    environment = os.getenv('ENVIRONMENT', 'development')
    
    if environment == 'development' and os.getenv('USE_LOCAL_WEBAPP') == 'true':
        localhost_port = os.getenv('LOCALHOST_PORT', '3000')
        webapp_url = f'https://localhost:{localhost_port}'
    elif environment == 'staging':
        webapp_url = 'https://meet-when-ah-git-staging.vercel.app'
    else:
        webapp_url = os.getenv('WEBAPP_URL', 'https://meet-when-ah.vercel.app')
    
    if params:
        query_string = urlencode(params)
        return f"{webapp_url}/{path}?{query_string}"
    else:
        return f"{webapp_url}/{path}"
