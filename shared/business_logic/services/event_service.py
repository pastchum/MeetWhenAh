from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import uuid

# Import from scheduler
from .scheduler import Scheduler

class EventService:
    """Business logic for event operations"""
    
    def __init__(self, database_service):
        """
        Initialize event service with database service
        
        Args:
            database_service: Database service for direct database operations
        """
        self.db = database_service
    
    def get_event(self, event_id: str) -> Optional[Dict[str, Any]]:
        """Get event details by ID"""
        try:
            event_data = self.db.getEntry("events", "event_id", event_id)
            return event_data
        except Exception as e:
            print(f"Error getting event {event_id}: {e}")
            return None
    
    def create_event(
        self, 
        name: str, 
        description: str, 
        start_date: str, 
        end_date: str, 
        creator_tele_id: str,
        auto_join: bool = True,
        event_type: str = "general",
        start_hour: str = "00:00:00.000000+08:00",
        end_hour: str = "23:30:00.000000+08:00"
    ) -> Optional[str]:
        """Create a new event and return its ID"""
        try:
            # Get creator details
            creator_data = self.db.getEntry("users", "tele_id", creator_tele_id)
            if not creator_data:
                print(f"Creator not found: {creator_tele_id}")
                return None
            
            creator_uuid = creator_data.get("uuid")
            if not creator_uuid:
                print(f"Creator UUID not found: {creator_tele_id}")
                return None
            
            event_id = str(uuid.uuid4())
            event_data = {
                "event_id": event_id,
                "event_name": name,
                "event_description": description,
                "event_type": event_type,
                "start_date": datetime.strptime(start_date, "%Y-%m-%d").replace(tzinfo=timezone.utc).isoformat(),
                "end_date": datetime.strptime(end_date, "%Y-%m-%d").replace(tzinfo=timezone.utc).isoformat(),
                "start_hour": start_hour,
                "end_hour": end_hour,
                "creator": creator_uuid,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            
            success = self.db.setEntry("events", event_id, event_data)
            return event_id if success else None
        except Exception as e:
            print(f"Error creating event: {e}")
            return None
    
    def join_event(self, event_id: str, user_tele_id: str) -> bool:
        """Add a user to an event's participants"""
        try:
            event = self.get_event(event_id)
            if not event:
                return False
            
            # Get user details
            user_data = self.db.getEntry("users", "tele_id", user_tele_id)
            if not user_data:
                return False
            
            user_uuid = user_data.get("uuid")
            if not user_uuid:
                return False
            
            # Get current event data
            current_event_data = self.db.getEntry("events", "event_id", event_id)
            if not current_event_data:
                return False
            
            # Check if user is already a participant
            participants = current_event_data.get("participants", [])
            if user_uuid not in participants:
                participants.append(user_uuid)
                
                return self.db.updateEntry("events", "event_id", event_id, {
                    "participants": participants
                })
            return True
        except Exception as e:
            print(f"Error joining event {event_id} for user {user_tele_id}: {e}")
            return False
    
    def get_event_sleep_preferences(self, event_id: str) -> Dict[str, Dict[str, str]]:
        """Get sleep preferences for all participants in an event"""
        try:
            event = self.get_event(event_id)
            if not event:
                return {}
            
            current_event_data = self.db.getEntry("events", "event_id", event_id)
            if not current_event_data:
                return {}
            
            sleep_prefs = {}
            participants = current_event_data.get("participants", [])
            
            for user_uuid in participants:
                user_data = self.db.getEntry("users", "uuid", user_uuid)
                if user_data and "sleep_start" in user_data and "sleep_end" in user_data:
                    sleep_prefs[user_uuid] = {
                        "start": user_data["sleep_start"],
                        "end": user_data["sleep_end"]
                    }
            
            return sleep_prefs
        except Exception as e:
            print(f"Error getting sleep preferences for event {event_id}: {e}")
            return {}
    
    def get_user_events(self, user_tele_id: str) -> List[Dict]:
        """Get all events that a user is a member of"""
        try:
            # Get user details
            user_data = self.db.getEntry("users", "tele_id", user_tele_id)
            if not user_data:
                return []
            
            user_uuid = user_data.get("uuid")
            if not user_uuid:
                return []
            
            # Get all events where user is a participant
            all_events = self.db.getEntries("events", "participants", user_uuid)
            if not all_events:
                return []
            
            events = []
            for event_data in all_events:
                events.append({
                    'id': event_data.get('event_id'),
                    'name': event_data.get('event_name', 'Unnamed Event')
                })
            
            return events
        except Exception as e:
            print(f"Error getting events for user {user_tele_id}: {e}")
            return []
    
    def get_event_best_time(self, event_id: str) -> List[Dict]:
        """Get the best time for an event using the scheduler"""
        try:
            scheduler = Scheduler()
            
            availability_blocks = self.db.getEntries("availability_blocks", "event_id", event_id)
            if not availability_blocks:
                return []
            
            best_event_blocks = scheduler._process_availability_blocks(availability_blocks)
            
            return best_event_blocks
        except Exception as e:
            print(f"Error getting best time for event {event_id}: {e}")
            return [] 