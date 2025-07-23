from fastapi import FastAPI, Request, Response
from pydantic import BaseModel
import uvicorn
from dotenv import load_dotenv
import os
import json
from fastapi.middleware.cors import CORSMiddleware

# Import handlers
from telegram.handlers.event_handlers import handle_event_confirmation

# Import services
from services.database_service import getEntry
from services.event_service import get_event_best_time

from telebot.types import Update

from scheduler.scheduler import Scheduler

# Import bot instance (we'll need to set up the import path correctly)
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from telegram.config.config import bot

# Initialize FastAPI app
app = FastAPI(title="MeetWhenAh API")

# cors
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# FastAPI models for API endpoints
class AvailabilityRequest(BaseModel):
    tele_id: str
    event_id: str
    availability_data: list = None

class WebhookUpdate(BaseModel):
    """Model for Telegram webhook updates"""
    update_id: int
    message: dict = None
    edited_message: dict = None
    channel_post: dict = None
    edited_channel_post: dict = None
    inline_query: dict = None
    callback_query: dict = None

# New webhook endpoint for Telegram
@app.post("/webhook/bot")
async def telegram_webhook(request: Request):
    """Handle Telegram webhook updates"""
    try:
        # Get the raw request body
        update_dict = await request.json()
        update = Update.de_json(update_dict)
        
        print("Update received: ", update)
        
        # Process the update
        bot.process_new_updates([update])
        
        return Response(status_code=200)
        
    except Exception as e:
        print(f"Error processing webhook update: {e}")
        return Response(status_code=500)

# Health check endpoint
@app.get("/webhook/health")
async def health_check():
    """Health check endpoint for the webhook"""
    return {"status": "healthy"}

@app.post("/api/event/confirm")
async def confirm_event(request: Request):
    """Confirm an event"""
    data = await request.json()
    event_id = data.get("event_id")
    best_start_time = data.get("best_start_time")
    best_end_time = data.get("best_end_time")

    # process confirm event
    success = handle_event_confirmation(event_id, best_start_time, best_end_time)
    return {"success": success}

@app.post("/api/event/get-best-time")
async def get_best_time(request: Request):
    """Get the best time for an event"""
    data = await request.json()
    event_id = data.get("event_id")
    best_time = get_event_best_time(event_id)
    print("best_time", best_time)
    return {"data": best_time}

if __name__ == "__main__":
    # Load environment variables
    load_dotenv()
    
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