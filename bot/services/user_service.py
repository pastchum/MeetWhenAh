"""User service — business logic for user operations."""

from datetime import datetime, timezone
from typing import Optional, Dict, Any
import uuid

from services.database_service import getEntry, parse_row, setEntry, updateEntry
from database.sqlmodels import UserCreatePayload, UserRow, UserUpdatePayload


def getUser(tele_id: str) -> Optional[Dict[str, Any]]:
    """Get a user by their Telegram ID"""
    try:
        user = parse_row(getEntry("users", "tele_id", str(tele_id)), UserRow)
        return user.model_dump(mode="json") if user else None
    except Exception as e:
        print(f"Error getting user {tele_id}: {e}")
        return None


def getUserFromUuid(user_uuid: str) -> Optional[Dict[str, Any]]:
    """Get a user by their UUID"""
    try:
        user = parse_row(getEntry("users", "uuid", user_uuid), UserRow)
        return user.model_dump(mode="json") if user else None
    except Exception as e:
        print(f"Error getting user by uuid {user_uuid}: {e}")
        return None


def setUser(tele_id: str, username: str) -> bool:
    """Create a new user"""
    try:
        user_uuid = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        user_data = UserCreatePayload(
            uuid=user_uuid,
            tele_id=str(tele_id),
            tele_user=username,
            initialised=False,
            callout_cleared=False,
            created_at=now,
            updated_at=now,
        )
        return setEntry("users", user_uuid, user_data)
    except Exception as e:
        print(f"Error setting user {tele_id}: {e}")
        return False


def updateUser(tele_id: str, **fields) -> bool:
    """Update arbitrary user fields by tele_id."""
    try:
        if not fields:
            return True
        fields["updated_at"] = datetime.now(timezone.utc).isoformat()
        validated_fields = UserUpdatePayload.model_validate(fields)
        return updateEntry("users", "tele_id", str(tele_id), validated_fields)
    except Exception as e:
        print(f"Error updating user {tele_id}: {e}")
        return False


def updateUserInitialised(tele_id: str) -> bool:
    """Mark a user as initialised with callout cleared"""
    return updateUser(tele_id, initialised=True, callout_cleared=True)


def updateUserCalloutCleared(tele_id: str) -> bool:
    """Mark a user's callout as cleared"""
    return updateUser(tele_id, callout_cleared=True)


def updateUsername(tele_id: str, username: str) -> bool:
    """Update or create a user's username"""
    try:
        user = getUser(tele_id)
        if user:
            return updateUser(tele_id, tele_user=username)
        else:
            return setUser(tele_id, username)
    except Exception as e:
        print(f"Error updating username for {tele_id}: {e}")
        return False


def setUserSleepPreferences(tele_id: str, sleep_start: str, sleep_end: str) -> bool:
    """Set a user's sleep preferences"""
    try:
        user = getUser(tele_id)
        if user:
            return updateUser(
                tele_id,
                sleep_start_time=sleep_start,
                sleep_end_time=sleep_end,
            )
        else:
            now = datetime.now(timezone.utc).isoformat()
            user_data = UserCreatePayload(
                uuid=str(uuid.uuid4()),
                tele_id=str(tele_id),
                tele_user="",
                initialised=False,
                callout_cleared=False,
                sleep_start_time=sleep_start,
                sleep_end_time=sleep_end,
                created_at=now,
                updated_at=now,
            )
            return setEntry("users", user_data.uuid, user_data)
    except Exception as e:
        print(f"Error setting sleep preferences for {tele_id}: {e}")
        return False
