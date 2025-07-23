from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
from collections import defaultdict

class AvailabilityService:
    """Business logic for availability operations"""
    
    def __init__(self, database_service):
        """
        Initialize availability service with database service
        
        Args:
            database_service: Database service for direct database operations
        """
        self.db = database_service
    
    def get_user_availability(self, tele_id: str, event_id: str) -> List[Dict[str, Any]]:
        """Get a user's availability for an event"""
        try:
            # Get user details
            user_data = self.db.getEntry("users", "tele_id", tele_id)
            if not user_data:
                return []
            
            user_uuid = user_data.get("uuid")
            if not user_uuid:
                return []
            
            # Get availability blocks for the event
            availability_blocks = self.db.getEntries("availability_blocks", "event_id", event_id)
            if not availability_blocks:
                return []
            
            # Filter for this user's availability
            user_availability = [
                block for block in availability_blocks 
                if block.get("user_uuid") == user_uuid
            ]
            
            return user_availability
        except Exception as e:
            print(f"Error getting availability for user {tele_id} in event {event_id}: {e}")
            return []
    
    def update_user_availability(
        self, 
        tele_id: str, 
        event_id: str, 
        availability_data: List[Dict]
    ) -> bool:
        """Update a user's availability for an event"""
        try:
            # Get user details
            user_data = self.db.getEntry("users", "tele_id", tele_id)
            if not user_data:
                return False
            
            user_uuid = user_data.get("uuid")
            if not user_uuid:
                return False
            
            # Delete all existing availability blocks for this user and event
            delete_success = self.db.deleteEntries(
                "availability_blocks", 
                "event_id", 
                event_id, 
                "user_uuid", 
                [user_uuid]
            )
            
            if not delete_success:
                return False
            
            # If no new availability data, we're done
            if not availability_data:
                return True
            
            # Transform availability data to include user_uuid and convert to scheduler format
            new_availability_data = []
            for item in availability_data:
                # Transform from {date: "2023-11-15", time: "1430"} to scheduler format
                date = item.get("date")
                time = item.get("time")
                
                if date and time:
                    # Convert time from "1430" format to "14:30:00" format
                    hours = int(time) // 100
                    minutes = int(time) % 100
                    time_formatted = f"{hours:02d}:{minutes:02d}:00"
                    
                    # Create start_time and end_time for 30-minute blocks with timezone
                    start_dt = datetime.strptime(f"{date} {time_formatted}", "%Y-%m-%d %H:%M:%S")
                    # Assume UTC timezone if not specified
                    start_dt = start_dt.replace(tzinfo=timezone.utc)
                    end_dt = start_dt + timedelta(minutes=30)
                    
                    # Format as ISO strings with timezone
                    start_time = start_dt.isoformat()
                    end_time = end_dt.isoformat()
                    
                    block_data = {
                        "start_time": start_time,
                        "end_time": end_time,
                        "event_id": event_id,
                        "user_uuid": user_uuid
                    }
                    new_availability_data.append(block_data)
            
            # Insert new availability data
            return self.db.setEntries("availability_blocks", new_availability_data)
        except Exception as e:
            print(f"Error updating availability for user {tele_id} in event {event_id}: {e}")
            return False
    
    def get_event_availability(self, event_id: str) -> Dict[str, List[Dict[str, Any]]]:
        """Get all availability data for an event, grouped by user"""
        try:
            # Get all availability blocks for the event
            availability_blocks = self.db.getEntries("availability_blocks", "event_id", event_id)
            if not availability_blocks:
                return {}
            
            # Group by user
            availability_by_user = defaultdict(list)
            
            for block in availability_blocks:
                user_uuid = block.get("user_uuid")
                if user_uuid:
                    # Get user details
                    user_data = self.db.getEntry("users", "uuid", user_uuid)
                    if user_data:
                        tele_id = user_data.get("tele_id")
                        availability_by_user[tele_id].append(block)
            
            return dict(availability_by_user)
        except Exception as e:
            print(f"Error getting event availability for {event_id}: {e}")
            return {}
    
    def format_availability_summary(self, event_id: str, tele_id: str) -> str:
        """Format a summary of a user's availability for an event"""
        try:
            # Get event details
            event_data = self.db.getEntry("events", "event_id", event_id)
            if not event_data:
                return "Event not found"
            
            # Get user availability
            user_availability = self.get_user_availability(tele_id, event_id)
            if not user_availability:
                return "No availability data found"
            
            # Format the summary
            event_name = event_data.get("event_name", "Unknown Event")
            summary = f"Your availability for {event_name}:\n\n"
            
            # Group availability by date
            by_date = defaultdict(list)
            for availability in user_availability:
                start_time = availability.get("start_time", "")
                if start_time:
                    # Extract date from start_time
                    date = start_time.split(" ")[0] if " " in start_time else start_time
                    time = start_time.split(" ")[1] if " " in start_time else start_time
                    by_date[date].append(time)
            
            # Format each date's availability
            for date in sorted(by_date.keys()):
                summary += f"{date}:\n"
                for time in sorted(by_date[date]):
                    summary += f"  {time}\n"
                summary += "\n"
            
            return summary
        except Exception as e:
            print(f"Error formatting availability summary: {e}")
            return "Error formatting availability summary" 