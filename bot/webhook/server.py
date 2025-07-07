from fastapi import FastAPI, Request, Response
from pydantic import BaseModel
import uvicorn
from dotenv import load_dotenv
import os
import json

# Import services
from telegram.handlers.availability_handlers import getUserAvailability, updateUserAvailability
from telegram.services.database_service import getEntry
from telegram.services.event_service import getEvent

# Import bot instance (we'll need to set up the import path correctly)
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from bot.telegram.config.config import bot

# Initialize FastAPI app
app = FastAPI(title="MeetWhenAh API")

# FastAPI models for API endpoints
class AvailabilityRequest(BaseModel):
    username: str
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

# New webhook endpoint for Telegram
@app.post("/webhook/bot")
async def telegram_webhook(request: Request):
    """Handle Telegram webhook updates"""
    try:
        # Get the raw request body
        body = await request.body()
        
        # Parse the update
        update = json.loads(body)
        
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