from datetime import datetime, timezone
from typing import Optional, Dict, Any
import uuid

class UserService:
    """Business logic for user operations"""
    
    def __init__(self, database_service):
        """
        Initialize user service with database service
        
        Args:
            database_service: Database service for direct database operations
        """
        self.db = database_service
    
    def getUser(self, tele_id: str) -> Optional[Dict[str, Any]]:
        """Get a user by their Telegram ID"""
        try:
            user = self.db.getEntry("users", "tele_id", tele_id)
            return user
        except Exception as e:
            print(f"Error getting user {tele_id}: {e}")
            return None
    
    def setUser(self, tele_id: str, username: str) -> bool:
        """Set a user by their Telegram ID"""
        try:
            user_uuid = str(uuid.uuid4())
            user_data = {
                "uuid": user_uuid,
                "tele_id": tele_id,
                "tele_user": username,
                "initialised": True,
                "callout_cleared": True,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            
            return self.db.setEntry("users", user_uuid, user_data)
        except Exception as e:
            print(f"Error setting user {tele_id}: {e}")
            return False
    
    def updateUserInitialised(self, tele_id: str) -> bool:
        """Update a user's initialised status"""
        try:
            success1 = self.db.updateEntry("users", "tele_id", tele_id, "initialised", True)
            success2 = self.db.updateEntry("users", "tele_id", tele_id, "callout_cleared", True)
            return success1 and success2
        except Exception as e:
            print(f"Error updating user initialised status {tele_id}: {e}")
            return False
    
    def updateUsername(self, tele_id: str, username: str) -> bool:
        """Update or create a user's username"""
        try:
            user = self.db.getEntry("users", "tele_id", tele_id)
            
            if user:
                # Update existing user
                user_data = user.copy()
                user_data["username"] = username
                user_data["updated_at"] = datetime.now(timezone.utc).isoformat()
                return self.db.updateEntry("users", tele_id, user_data)
            else:
                # Create new user
                return self.setUser(tele_id, username)
        except Exception as e:
            print(f"Error updating username for {tele_id}: {e}")
            return False
    
    def setUserSleepPreferences(self, tele_id: str, sleep_start: str, sleep_end: str) -> bool:
        """Set a user's sleep preferences"""
        try:
            user = self.db.getEntry("users", "tele_id", tele_id)
            
            if user:
                # Update existing user
                user_data = user.copy()
            else:
                # Create new user
                user_data = {
                    "tele_id": tele_id,
                    "created_at": datetime.now(timezone.utc).isoformat()
                }
            
            # Update sleep preferences
            user_data.update({
                "sleep_start": sleep_start,
                "sleep_end": sleep_end,
                "updated_at": datetime.now(timezone.utc).isoformat()
            })
            
            if user:
                return self.db.updateEntry("users", tele_id, user_data)
            else:
                return self.db.setEntry("users", tele_id, user_data)
        except Exception as e:
            print(f"Error setting sleep preferences for {tele_id}: {e}")
            return False
    
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get a user by their username"""
        try:
            user_data = self.db.getEntry("users", "tele_user", username)
            return user_data
        except Exception as e:
            print(f"Error getting user by username {username}: {e}")
            return None 