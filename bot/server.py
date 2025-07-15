from fastapi import FastAPI, Request, Response
from pydantic import BaseModel
import uvicorn
from dotenv import load_dotenv
import os
import json
from fastapi.middleware.cors import CORSMiddleware

# Import services
from telegram.services.database_service import getEntry
from telegram.services.event_service import getEvent, getUserAvailability, updateUserAvailability

from telebot.types import Update

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

# API endpoints
@app.get('/api/availability/{tele_id}/{event_id}')
async def get_availability(tele_id: str, event_id: str):
    availability = getUserAvailability(tele_id, event_id)

    return {"status": "success", "data": availability}

@app.post('/api/save-availability')
async def update_availability(request: AvailabilityRequest):
    success = updateUserAvailability(
        request.tele_id,
        request.event_id,
        request.availability_data
    )
    
    if success:
        return {"status": "success", "message": "Availability updated successfully"}
    else:
        return {"status": "error", "message": "Failed to update availability"}

@app.get('/api/event/{event_id}')
async def get_event(event_id: str):
    event_data = getEntry("events", "event_id", str(event_id))
    
    if not event_data:
        return {"status": "error", "message": "Event not found"}
    
    return {"status": "success", "data": event_data}

@app.get('/api/user/user-data-from-tele-id/{tele_id}')
async def get_user_data_from_tele_id(tele_id: str):
    """Get user UUID, username and telegram id from telegram id"""
    user_data = getEntry("users", "tele_id", tele_id)
    
    if not user_data:
        return {"status": "error", "message": "User not found"}
    
    return {"status": "success", "data": {"uuid": user_data.get("uuid"), "username": user_data.get("username")}}

@app.get('/api/user/user-data-from-username/{username}')
async def get_user_data_from_username(username: str):
    """Get user UUID, username and telegram id from username"""
    user_data = getEntry("users", "tele_user", username)
    
    if not user_data:
        return {"status": "error", "message": "User not found"}
    
    return {"status": "success", "data": {"uuid": user_data.get("uuid"), "username": user_data.get("username"), "tele_id": user_data.get("tele_id")}}

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