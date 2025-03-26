import uvicorn
from telegram import app

if __name__ == "__main__":
    print("Starting FastAPI server...")
    print("API endpoints available at http://localhost:8000")
    print("Available endpoints:")
    print("  - GET /api/availability/{username}/{event_id} - Get user availability")
    print("  - POST /api/availability - Update user availability")
    print("  - GET /api/event/{event_id} - Get event details")
    print("\nBot commands available in Telegram:")
    print("  - /start - Create a new event")
    print("  - /sleep - Set your sleep hours")
    print("  - /myavailability - Check your availability for an event")
    print("  - /updateavailability - Update your availability for an event")
    
    uvicorn.run(app, host="0.0.0.0", port=8000) 