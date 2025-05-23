from dotenv import load_dotenv
import telebot
from telebot import types
import logging
import os
import fastapi
from fastapi import Request
from pydantic import BaseModel
import uvicorn

# Import handlers
from handlers.event_handlers import register_event_handlers
from handlers.user_handlers import register_user_handlers
from handlers.availability_handlers import register_availability_handlers
from handlers.inline_handlers import register_inline_handlers

# Import services
from services.availability_service import getUserAvailability, updateUserAvailability
from services.user_service import getEntry

# Load environment variables
load_dotenv()
TOKEN = os.getenv('TOKEN')
WEBHOOK_URL_PATH = "/%s/" % (TOKEN)

# Setup logging
logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)

# Initialize bot
bot = telebot.TeleBot(TOKEN, parse_mode='HTML', threaded=False)

# Initialize FastAPI app
app = fastapi.FastAPI(docs=None, redoc_url=None)

# FastAPI models for API endpoints
class AvailabilityRequest(BaseModel):
    username: str
    event_id: str
    availability_data: list = None

# Empty webserver index
@app.get('/')
def index():
    return ''

# Webhook endpoint
@app.post(f'/{TOKEN}/')
def process_webhook(update: dict):
    """Process webhook calls"""
    if update:
        update = telebot.types.Update.de_json(update)
        bot.process_new_updates([update])
    else:
        return

# API endpoints
@app.get('/api/availability/{username}/{event_id}')
async def get_availability(username: str, event_id: str):
    availability = getUserAvailability(username, event_id)
    if availability:
        return {"status": "success", "data": availability}
    else:
        return {"status": "error", "message": "Could not retrieve availability"}

@app.post('/api/availability')
async def update_availability(request: AvailabilityRequest):
    success = updateUserAvailability(
        request.username,
        request.event_id,
        request.availability_data
    )
    
    if success:
        return {"status": "success", "message": "Availability updated successfully"}
    else:
        return {"status": "error", "message": "Failed to update availability"}

@app.get('/api/event/{event_id}')
async def get_event(event_id: str):
    event_doc = getEntry("Events", "event_id", str(event_id))
    
    if not event_doc:
        return {"status": "error", "message": "Event not found"}
        
    event_data = event_doc.to_dict()
    
    # Format dates for JSON serialization
    if "start_date" in event_data:
        event_data["start_date"] = event_data["start_date"].strftime("%Y-%m-%d")
    if "end_date" in event_data:
        event_data["end_date"] = event_data["end_date"].strftime("%Y-%m-%d")
        
    # Format hours_available dates
    for day in event_data.get("hours_available", []):
        if "date" in day and hasattr(day["date"], "strftime"):
            day["date"] = day["date"].strftime("%Y-%m-%d")
    
    return {"status": "success", "data": event_data}

def register_handlers():
    """Register all bot handlers"""
    register_event_handlers(bot)
    register_user_handlers(bot)
    register_availability_handlers(bot)
    register_inline_handlers(bot)

# Start the bot if running directly
if __name__ == "__main__":
    logger.info("Starting Telegram bot polling...")
    register_handlers()
    bot.polling(none_stop=True)
else:
    # When imported as a module, don't start polling
    logger.info("Telegram bot loaded as module")
    register_handlers() 