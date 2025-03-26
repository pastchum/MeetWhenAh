import os
import sys
import threading
import uvicorn
import time
import logging
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Configure logging first
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    # Import bot and handlers
    from src.config.config import bot
    from src.handlers import command_handlers, event_handlers, availability_handlers, inline_handlers
    from fastapi import FastAPI
    
    logger.info("Successfully imported all required modules")
except ImportError as e:
    logger.error(f"Failed to import required modules: {e}")
    sys.exit(1)

# Create FastAPI app
app = FastAPI()

def run_telegram_bot():
    """Run the Telegram bot polling in a thread."""
    logger.info("Starting Telegram bot polling...")
    try:
        # Log registered handlers for debugging
        logger.info("Registered message handlers: %s", bot.message_handlers)
        logger.info("Registered command handlers: %s", [handler.commands for handler in bot.message_handlers if hasattr(handler, 'commands')])
        bot.infinity_polling(timeout=60, long_polling_timeout=60)
    except Exception as e:
        logger.error(f"Error in Telegram bot: {e}")
        
def run_fastapi_server():
    """Run the FastAPI server in a thread."""
    logger.info("Starting FastAPI server...")
    try:
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
    except Exception as e:
        logger.error(f"Error in FastAPI server: {e}")

def main():
    """Main function to run the application."""
    try:
        # Print info
        print("=== Meet When Ah? Backend ===")
        print("\nStarting both Telegram bot and FastAPI server...")
        print("\nAPI endpoints available at http://localhost:8000:")
        print("  - GET /api/availability/{username}/{event_id} - Get user availability")
        print("  - POST /api/availability - Update user availability")
        print("  - GET /api/event/{event_id} - Get event details")
        print("\nBot commands available in Telegram:")
        print("  - /start - Create a new event")
        print("  - /sleep - Set your sleep hours")
        print("  - /myavailability - Check your availability for an event")
        print("  - /updateavailability - Update your availability for an event")
        
        # Create threads
        telegram_thread = threading.Thread(target=run_telegram_bot)
        telegram_thread.daemon = True
        
        # Start threads
        telegram_thread.start()
        logger.info("Telegram bot thread started")
        
        # Run FastAPI in the main thread
        run_fastapi_server()
        
        # This won't be reached until the FastAPI server is stopped
        telegram_thread.join()
        
    except Exception as e:
        logger.error(f"Error in main: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 