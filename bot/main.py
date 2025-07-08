import uvicorn
import threading
import os
from dotenv import load_dotenv

from telegram_bot import initialise_bot
from server import app

def run_server():
    # Get port from environment or default to 8000
    port = int(os.getenv("PORT", 8000))
    
    # Get SSL certificate paths if available
    ssl_certfile = os.getenv("SSL_CERTFILE")
    ssl_keyfile = os.getenv("SSL_KEYFILE")
    
    # Start the FastAPI server with SSL if certificates are available
    if ssl_certfile and ssl_keyfile:
        uvicorn.run(
            app, 
            host="0.0.0.0", 
            port=port,
            ssl_certfile=ssl_certfile,
            ssl_keyfile=ssl_keyfile
        )
    else:
        uvicorn.run(app, host="0.0.0.0", port=port)

def main():
    # Start the FastAPI server in a separate thread
    # Load environment variables
    load_dotenv()
    
    run_server()
    # Start the Telegram bot in the main thread
    initialise_bot()

if __name__ == "__main__":
    main()