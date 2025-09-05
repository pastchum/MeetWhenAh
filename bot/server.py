from fastapi import FastAPI, Request, Response, Header, HTTPException, status
from pydantic import BaseModel
import uvicorn
from dotenv import load_dotenv
import os
import json
import logging
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware

# Import handlers
from telegram.handlers.event_handlers import handle_event_confirmation

# Import services
from services.event_service import get_event_best_time, getEvent, getConfirmedEvent, generate_confirmed_event_description, generate_event_description
from services.reminder_service import send_daily_availability_reminders, send_daily_event_reminders, send_upcoming_event_reminders
from services.share_service import get_ctx, handle_share_event, set_chat

from telebot.types import Update

# Import bot instance (we'll need to set up the import path correctly)
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from telegram.config.config import bot

# Initialize FastAPI app
app = FastAPI(title="MeetWhenAh API")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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


@app.post("/api/share")
async def share_event(request: Request):
    """Share an event"""
    data = await request.json()
    token = data["token"]
    event_id = data["event_id"]

    # get the event
    event = getEvent(event_id)
    if not event:
        return {"error": "Event not found"}

    # get the event chat details
    ctx = get_ctx(token)
    if not ctx:
        return {"error": "Invalid token"}
    print("ctx", ctx)
    # edit the message
    success = handle_share_event(event_id, ctx["tele_id"], ctx["chat_id"], ctx["message_id"], ctx["thread_id"])
    if not success:
        return {"error": "Failed to handle share event"}
    
    return {"success": True}

@app.post("/api/event/confirm")
async def confirm_event(request: Request):
    """Confirm an event"""
    data = await request.json()
    event_id = data["event_id"]
    best_start_time = data["best_start_time"]
    best_end_time = data["best_end_time"]

    # process confirm event
    success = handle_event_confirmation(event_id, best_start_time, best_end_time)
    return {"success": success}

@app.post("/api/event/get-best-time")
async def get_best_time(request: Request):
    """Get the best time for an event"""
    data = await request.json()
    event_id = data["event_id"]
    best_time = get_event_best_time(event_id)
    print("best_time", best_time)
    return {"data": best_time}

@app.post("/api/dashboard/log")
async def log_dashboard_access(request: Request):
    """Log dashboard access for analytics and debugging"""
    try:
        data = await request.json()
        
        # Get client IP and user agent
        client_ip = request.client.host
        user_agent = request.headers.get("user-agent", "unknown")
        
        # Enhanced logging data
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": "dashboard_access",
            "client_ip": client_ip,
            "user_agent": user_agent,
            "telegram_data": data,
            "server_logged_at": datetime.now().isoformat()
        }
        
        # Log to console (this will appear in your server logs)
        logger.info(f"📊 Dashboard Access Logged: {json.dumps(log_entry, indent=2)}")
        print(f"📊 Dashboard Access Logged: {json.dumps(log_entry, indent=2)}")
        
        # You can also store this in a database or send to analytics service here
        
        return {"success": True, "message": "Dashboard access logged successfully"}
        
    except Exception as e:
        logger.error(f"❌ Error logging dashboard access: {e}")
        print(f"❌ Error logging dashboard access: {e}")
        return {"success": False, "error": str(e)}

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

    return {"success": True}

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