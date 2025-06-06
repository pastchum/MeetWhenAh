import os
import sys
import signal
from dotenv import load_dotenv
import logging

# Import handlers
from handlers.event_handlers import register_event_handlers
from handlers.user_handlers import register_user_handlers
from handlers.availability_handlers import register_availability_handlers
from handlers.inline_handlers import register_inline_handlers

# Import bot instance from config
from config.config import bot, logger

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    print("\nSignal received. Cleaning up...")
    try:
        # Clear any pending handlers
        bot.stop_polling()
        # Remove webhook if any
        bot.remove_webhook()
    except Exception as e:
        print(f"Error during cleanup: {e}")
    sys.exit(0)

def setup_bot():
    """Setup the bot with proper configuration."""
    try:
        # Remove any existing webhook
        bot.remove_webhook()
        # Clear any pending updates
        bot.get_updates(offset=-1)
        # Clear any step handlers
        bot._step_handlers = {}
        print("Bot setup completed successfully.")
    except Exception as e:
        print(f"Error during bot setup: {e}")
        sys.exit(1)

def register_handlers():
    """Register all bot handlers"""
    register_event_handlers(bot)
    register_user_handlers(bot)
    register_availability_handlers(bot)
    register_inline_handlers(bot)

def main():
    """Main function to start the Telegram bot."""
    try:
        # Register signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Setup the bot
        setup_bot()
        
        # Register handlers
        register_handlers()
        
        logger.info("Starting bot...")
        bot.infinity_polling(timeout=60, long_polling_timeout=60)
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 