import uuid
from datetime import datetime
from services.database_service import getEntry, setEntry, supabase


"""
Class to represent a user in the system.

users Table Schema:
  uuid           UUID            PRIMARY KEY,
  tele_id        VARCHAR(64) unique,                  -- Telegram numeric ID (if any)
  tele_user      VARCHAR(255) unique,     -- Telegram username
  created_at      TIMESTAMPTZ       NOT NULL DEFAULT NOW(),
  updated_at      TIMESTAMPTZ       NOT NULL DEFAULT NOW(),
  initialised    boolean DEFAULT false,
  callout_cleared      boolean DEFAULT false,
  sleep_start_time     TIMETZ,
  sleep_end_time       TIMETZ,
  tmp_sleep_start      TIMETZ                      -- temporary override
"""

class User:
    user_uuid: str
    tele_id: str
    tele_user: str
    created_at: datetime
    updated_at: datetime
    initialised: bool
    callout_cleared: bool
    sleep_start_time: int
    sleep_end_time: int
    tmp_sleep_start: int

    def __init__(self, 
                    tele_id: str, 
                    tele_user: str, 
                    created_at: datetime, 
                    updated_at: datetime, 
                    initialised: bool = False,
                    callout_cleared: bool = True,
                    sleep_start_time: int = 2300,
                    sleep_end_time: int = 700,
                    tmp_sleep_start: int = 0,
                    user_uuid: str = str(uuid.uuid4())
):
            self.user_uuid = user_uuid
            self.tele_id = tele_id
            self.tele_user = tele_user
            self.created_at = created_at
            self.updated_at = updated_at
            self.initialised = initialised
            self.callout_cleared = callout_cleared
            self.sleep_start_time = sleep_start_time
            self.sleep_end_time = sleep_end_time
            self.tmp_sleep_start = tmp_sleep_start

    """Getters for user attributes"""
    def get_user_uuid(self) -> str:
        return self.user_uuid
    
    def get_tele_id(self) -> str:
        return self.tele_id
    
    def get_tele_user(self) -> str:
        return self.tele_user
    
    def get_created_at(self) -> datetime:
        return self.created_at
    
    def get_updated_at(self) -> datetime:
        return self.updated_at
    
    def is_initialised(self) -> bool:
        return self.initialised
    
    def is_callout_cleared(self) -> bool:
        return self.callout_cleared
    
    def get_sleep_start_time(self) -> int:
        return self.sleep_start_time
    
    def get_sleep_end_time(self) -> int:
        return self.sleep_end_time
    
    def get_tmp_sleep_start(self) -> int:
        return self.tmp_sleep_start
    
    """Functions to create user"""

    async def _create_user(
                tele_id: str, 
                tele_user: str, 
                created_at: datetime, 
                updated_at: datetime, 
                initialised: bool = False,
                callout_cleared: bool = True,
                sleep_start_time: int = 2300,
                sleep_end_time: int = 700,
                tmp_sleep_start: int = 0,
                user_uuid: str = str(uuid.uuid4())
    ):
        """Create a new user in the database"""
        user = User(
            tele_id=tele_id,
            tele_user=tele_user,
            created_at=created_at,
            updated_at=updated_at,
            initialised=initialised,
            callout_cleared=callout_cleared,
            sleep_start_time=sleep_start_time,
            sleep_end_time=sleep_end_time,
            tmp_sleep_start=tmp_sleep_start,
            user_uuid=user_uuid
        )
        # Insert into database
        user_data = {
            "uuid": user.user_uuid,
            "tele_id": user.tele_id,
            "tele_user": user.tele_user,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
            "initialised": user.initialised,
            "callout_cleared": user.callout_cleared,
            "sleep_start_time": user.sleep_start_time,
            "sleep_end_time": user.sleep_end_time,
            "tmp_sleep_start": user.tmp_sleep_start
        }
        success = setEntry("users", user_data)
        if not success:
            return None
        return user

    """Static methods for user operations"""
    @staticmethod
    def _from_database_by_uuid(user_uuid: str):
        """Fetch a user from the database by tele_id"""
        row = getEntry("users", "uuid", user_uuid)
        if not row:
            return None
        return User(
            user_uuid=row["uuid"],
            tele_id=row["tele_id"],
            tele_user=row["tele_user"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            initialised=row.get("initialised", False),
            callout_cleared=row.get("callout_cleared", True),
            sleep_start_time=row.get("sleep_start_time", 2300),
            sleep_end_time=row.get("sleep_end_time", 700),
            tmp_sleep_start=row.get("tmp_sleep_start", 0)
        )
    
    @staticmethod
    def _from_database_by_tele_id(tele_id: str):
        """Fetch a user from the database by tele_id"""
        row = getEntry("users", "tele_id", tele_id)
        if not row:
            return None
        return User(
            user_uuid=row["uuid"],
            tele_id=row["tele_id"],
            tele_user=row["tele_user"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            initialised=row.get("initialised", False),
            callout_cleared=row.get("callout_cleared", True),
            sleep_start_time=row.get("sleep_start_time", 2300),
            sleep_end_time=row.get("sleep_end_time", 700),
            tmp_sleep_start=row.get("tmp_sleep_start", 0)
        )
    

    @staticmethod
    def getUser(tele_id: str):
        """Get user by tele_id"""
        return User._from_database_by_tele_id(tele_id)
    
    @staticmethod
    def getUserFromUuid(user_uuid: str):
        """Get user by user_uuid"""
        return User._from_database_by_uuid(user_uuid)

    @staticmethod
    def create_user(tele_id: str, tele_user: str):
        """Static method to create a new user with current timestamp"""
        now = datetime.now()
        return User._create_user(
            tele_id=tele_id,
            tele_user=tele_user,
            created_at=now,
            updated_at=now
        )
    
    async def update_user(self, 
                    tele_user: str = None, 
                    initialised: bool = None,
                    callout_cleared: bool = None,
                    sleep_start_time: int = None,
                    sleep_end_time: int = None,
                    tmp_sleep_start: int = None
                ):
        """Update the user in the database"""
        self.updated_at = datetime.now()
        updated_data = {
            "tele_user": tele_user if tele_user is not None else self.tele_user,
            "updated_at": self.updated_at,
            "initialised": initialised if initialised is not None else self.initialised,
            "callout_cleared": callout_cleared if callout_cleared is not None else self.callout_cleared,
            "sleep_start_time": sleep_start_time if sleep_start_time is not None else self.sleep_start_time,
            "sleep_end_time": sleep_end_time if sleep_end_time is not None else self.sleep_end_time,
            "tmp_sleep_start": tmp_sleep_start if tmp_sleep_start is not None else self.tmp_sleep_start
        }
        return supabase.table("users").update(updated_data).eq("uuid", self.user_uuid).execute()
    
