import uvicorn
import threading
from telegram_bot import initialise_bot
from server import app

def run_server():
    uvicorn.run(app, host='0.0.0.0', port=8000)

def main():
    # Start the FastAPI server in a separate thread
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()
    
    # Start the Telegram bot in the main thread
    initialise_bot()

if __name__ == "__main__":
    main()