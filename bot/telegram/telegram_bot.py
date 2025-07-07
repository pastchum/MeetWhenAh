import os
import sys
import signal
from dotenv import load_dotenv
import logging

# Import handlers
from telegram.handlers.event_handlers import register_event_handlers
from telegram.handlers.user_handlers import register_user_handlers
from telegram.handlers.availability_handlers import register_availability_handlers
from telegram.handlers.inline_handlers import register_inline_handlers

# Import bot instance and configs
from telegram.config.config import bot, logger
from telegram.config.webhook_config import setup_webhook, remove_webhook, get_webhook_info

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    print("\nSignal received. Cleaning up...")
    try:
        # Clear any pending handlers
        bot.stop_polling()
        # Remove webhook if any
        remove_webhook()
    except Exception as e:
        print(f"Error during cleanup: {e}")
    sys.exit(0)

def setup_bot(use_webhook=False):
    """Setup the bot with proper configuration."""
    try:
        # Remove any existing webhook
        remove_webhook()
        
        if use_webhook:
            # Setup webhook if URL is configured
            webhook_url = os.getenv('WEBHOOK_URL')
            if webhook_url:
                success = setup_webhook(webhook_url)
                if success:
                    logger.info("Webhook setup completed successfully")
                    return True
                else:
                    logger.warning("Webhook setup failed, falling back to polling")
                    return False
            else:
                logger.warning("No webhook URL configured, falling back to polling")
                return False
        else:
            # Clear any pending updates when using polling
            bot.get_updates(offset=-1)
            logger.info("Polling setup completed successfully")
            return True
            
    except Exception as e:
        logger.error(f"Error during bot setup: {e}")
        sys.exit(1)

def register_handlers():
    """Register all bot handlers"""
    register_event_handlers(bot)
    register_user_handlers(bot)
    register_availability_handlers(bot)
    register_inline_handlers(bot)

def initialise_bot():
    """Main function to start the Telegram bot."""
    try:
        # Register signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Check if webhook is configured
        use_webhook = bool(os.getenv('USE_WEBHOOK', 'false').lower() == 'true')
        
        # Setup the bot
        setup_successful = setup_bot(use_webhook)
        
        # Register handlers
        register_handlers()
        
        if use_webhook and setup_successful:
            logger.info("Starting bot with webhook...")

        else:
            # Fall back to polling
            logger.info("Starting bot with polling...")
            bot.infinity_polling(timeout=60, long_polling_timeout=60)
            
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    initialise_bot() 