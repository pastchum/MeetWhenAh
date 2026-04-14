from dataclasses import dataclass, field
from typing import Optional
import uuid


@dataclass
class User:
    """Thin data class representing a user row. No DB logic."""

    tele_id: str
    tele_user: str
    user_uuid: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    initialised: bool = False
    callout_cleared: bool = False
    sleep_start_time: Optional[str] = None
    sleep_end_time: Optional[str] = None
    tmp_sleep_start: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        """Build a User from a database row dict."""
        return cls(
            user_uuid=data.get("uuid", str(uuid.uuid4())),
            tele_id=data.get("tele_id", ""),
            tele_user=data.get("tele_user", ""),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            initialised=data.get("initialised", False),
            callout_cleared=data.get("callout_cleared", False),
            sleep_start_time=data.get("sleep_start_time"),
            sleep_end_time=data.get("sleep_end_time"),
            tmp_sleep_start=data.get("tmp_sleep_start"),
        )
