from fastapi import FastAPI, Request, Header, HTTPException, status
from pydantic import BaseModel
import uvicorn
from dotenv import load_dotenv
import os
import json
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

# Import events
from events.events import Event

# Import handlers
from telegram.handlers.event_handlers import handle_event_confirmation

# Import services
from services.event_service import get_event_best_time, getEvent, getConfirmedEvent, generate_confirmed_event_description, generate_event_description
from services.reminder_service import send_daily_availability_reminders, send_daily_event_reminders, send_upcoming_event_reminders
from services.share_service import get_ctx, handle_share_event, set_chat
from services.user_service import getUser

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
        
        return JSONResponse(status_code=200)
        
    except Exception as e:
        print(f"Error processing webhook update: {e}")
        return JSONResponse(status_code=500)

# Health check endpoint
@app.get("/webhook/health")
async def health_check():
    """Health check endpoint for the webhook"""
    return {"status": "healthy"}


@app.post("/api/share")
async def share_event(request: Request):
    """Share an event"""
    data = await request.json()
    token = data["token"]
    event_id = data["event_id"]

    # get the event
    event = getEvent(event_id)
    if not event:
        return JSONResponse(status_code=400, content=jsonable_encoder({"error": "Event not found"}))

    # get the event chat details
    ctx = get_ctx(token)
    if not ctx:
        return JSONResponse(status_code=400, content=jsonable_encoder({"error": "Invalid token"}))
    print("ctx", ctx)
    # edit the message
    success = handle_share_event(event_id, ctx["tele_id"], ctx["chat_id"], ctx["message_id"], ctx["thread_id"])
    if not success:
        return JSONResponse(status_code=400, content=jsonable_encoder({"error": "Failed to handle share event"}))
    
    return JSONResponse(status_code=200, content=jsonable_encoder({"success": True}))

@app.post("/api/event/create")
async def create_event(request: Request):
    """Create an event"""
    data = await request.json()
    print("data", data)

    # get token details 
    token = data["token"]

    ctx = get_ctx(token)
    if not ctx:
        return JSONResponse(status_code=400, content=jsonable_encoder({"error": "Invalid token"})) 
    
    # get event details
    event_id = data["event_id"]
    event_name = data["event_name"]
    event_description = data["event_details"]
    event_type = data["event_type"]
    start_date = data["start"]
    end_date = data["end"]
    creator_tele_id = data["creator"]

    creator = getUser(creator_tele_id)
    if not creator:
        return JSONResponse(status_code=400, content=jsonable_encoder({"error": "Creator not found"}))
    creator_uuid = creator["uuid"]
    start_hour: str = "00:00:00.000000+08:00", 
    end_hour: str = "23:30:00.000000+08:00"
    min_participants = 2
    min_duration = 2
    max_duration = 4
    is_reminders_enabled = True
    timezone = "Asia/Singapore"

    event = await Event.create_event(
        event_id=event_id, 
        event_name=event_name, 
        event_description=event_description, 
        event_type=event_type, 
        start_date=start_date, 
        end_date=end_date, 
        start_hour=start_hour, 
        end_hour=end_hour, 
        creator=creator_uuid,
        min_participants=min_participants,
        min_duration=min_duration,
        max_duration=max_duration,
        is_reminders_enabled=is_reminders_enabled,
        timezone=timezone
        )
    if not event:
        return JSONResponse(status_code=400, content=jsonable_encoder({"error": "Failed to create event"}))
    
    # Share event
    success = handle_share_event(event_id, ctx["tele_id"], ctx["chat_id"], ctx["message_id"], ctx["thread_id"])
    if not success:
        return JSONResponse(status_code=400, content={"error": "Failed to share event"})
    
    return JSONResponse(status_code=200, content=jsonable_encoder({"event_id": event.get_event_id()}))


@app.post("/api/event/confirm")
async def confirm_event(request: Request):
    """Confirm an event"""
    data = await request.json()
    event_id = data["event_id"]
    best_start_time = data["best_start_time"]
    best_end_time = data["best_end_time"]

    # process confirm event
    success = handle_event_confirmation(event_id, best_start_time, best_end_time)
    return JSONResponse(status_code=200, content=jsonable_encoder({"success": success}))

@app.post("/api/event/get-best-time")
async def get_best_time(request: Request):
    """Get the best time for an event"""
    data = await request.json()
    event_id = data["event_id"]
    best_time = get_event_best_time(event_id)
    print("best_time", best_time)
    return JSONResponse(status_code=200, content=jsonable_encoder({"data": best_time}))

@app.post("/api/reminders")
async def send_reminders(api_key: str = Header(...)):
    """Send reminders for all events"""
    expected_key = os.getenv("REMINDER_API_KEY")
    if api_key != expected_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key"
        )

    send_daily_availability_reminders()
    send_daily_event_reminders()
    send_upcoming_event_reminders()

    return JSONResponse(status_code=200, content=jsonable_encoder({"success": True}))

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