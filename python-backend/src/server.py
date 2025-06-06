from fastapi import FastAPI, Request
from pydantic import BaseModel
import uvicorn
from dotenv import load_dotenv
import os

# Import services
from services.availability_service import getUserAvailability, updateUserAvailability
from services.event_service import getEvent
from services.user_service import getEntry

# Initialize FastAPI app
app = FastAPI(title="MeetWhenAh API")

# FastAPI models for API endpoints
class AvailabilityRequest(BaseModel):
    username: str
    event_id: str
    availability_data: list = None

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

if __name__ == "__main__":
    # Load environment variables
    load_dotenv()
    
    # Get port from environment or default to 8000
    port = int(os.getenv("PORT", 8000))
    
    # Start the FastAPI server
    uvicorn.run(app, host="0.0.0.0", port=port) 