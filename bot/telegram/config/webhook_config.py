import os
import logging
from ..config.config import bot, logger

def setup_webhook(url=None, certificate=None):
    """
    Set up webhook for the bot.
    
    Args:
        url (str): The HTTPS URL to send updates to. Defaults to environment variable.
        certificate (str): Path to public key certificate (optional)
    """
    try:
        # Get webhook URL from parameter or environment
        webhook_url = url or os.getenv('WEBHOOK_URL')
        logger.info(f"Attempting to set webhook with URL: {webhook_url}")
        
        if not webhook_url:
            logger.error("No webhook URL provided")
            return False
            
        # Validate URL format
        if not webhook_url.startswith('https://'):
            logger.error("Webhook URL must start with https://")
            return False
            
        # Remove existing webhook
        logger.info("Removing existing webhook...")
        bot.remove_webhook()
        
        # Set up new webhook
        logger.info(f"Setting up new webhook with URL: {webhook_url}")
        logger.info(f"Certificate provided: {bool(certificate)}")
        
        webhook_params = {
            'url': webhook_url,
            'certificate': open(certificate, 'r') if certificate else None,
            'max_connections': 40,
            'allowed_updates': ['message', 'callback_query', 'inline_query']
        }
        logger.debug(f"Webhook parameters: {webhook_params}")
        
        bot.set_webhook(**webhook_params)
        
        # Verify webhook info
        webhook_info = bot.get_webhook_info()
        logger.info("Webhook setup response:")
        logger.info(f"URL: {webhook_info.url}")
        logger.info(f"Has custom certificate: {webhook_info.has_custom_certificate}")
        logger.info(f"Pending update count: {webhook_info.pending_update_count}")
        logger.info(f"Last error date: {webhook_info.last_error_date}")
        logger.info(f"Last error message: {webhook_info.last_error_message}")
        logger.info(f"Max connections: {webhook_info.max_connections}")
        logger.info(f"IP address: {webhook_info.ip_address}")
        
        if webhook_info.last_error_message:
            logger.error(f"Webhook setup completed but has errors: {webhook_info.last_error_message}")
            return False
            
        logger.info("Webhook setup completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to set up webhook: {e}", exc_info=True)
        return False

def remove_webhook():
    """Remove the current webhook."""
    try:
        logger.info("Attempting to remove webhook...")
        current_webhook = bot.get_webhook_info()
        logger.info(f"Current webhook URL before removal: {current_webhook.url}")
        
        bot.remove_webhook()
        
        # Verify removal
        updated_webhook = bot.get_webhook_info()
        logger.info(f"Webhook URL after removal: {updated_webhook.url}")
        
        if not updated_webhook.url:
            logger.info("Webhook has been removed successfully")
            return True
        else:
            logger.warning(f"Webhook might not be fully removed. Current URL: {updated_webhook.url}")
            return False
    except Exception as e:
        logger.error(f"Failed to remove webhook: {e}", exc_info=True)
        return False

def get_webhook_info():
    """Get current webhook information."""
    try:
        webhook_info = bot.get_webhook_info()
        logger.info("\nCurrent Webhook Status:")
        logger.info(f"URL: {webhook_info.url}")
        logger.info(f"Has custom certificate: {webhook_info.has_custom_certificate}")
        logger.info(f"Pending update count: {webhook_info.pending_update_count}")
        logger.info(f"Last error date: {webhook_info.last_error_date}")
        logger.info(f"Last error message: {webhook_info.last_error_message}")
        logger.info(f"Max connections: {webhook_info.max_connections}")
        logger.info(f"IP address: {webhook_info.ip_address}")
        return webhook_info
    except Exception as e:
        logger.error(f"Failed to get webhook info: {e}", exc_info=True)
        return None 