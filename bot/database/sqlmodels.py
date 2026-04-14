"""SQLModel schemas for validating SQL row data and write payloads."""

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel


class EventType(str, Enum):
    """Supported event types persisted in the events table."""

    GENERAL = "general"

    @classmethod
    def _missing_(cls, value):
        # Keep backward compatibility for historical/custom DB values.
        return cls.GENERAL


class EventRow(SQLModel, table=False):
    event_id: str
    event_name: str
    event_description: str
    event_type: EventType = EventType.GENERAL
    start_date: datetime
    end_date: datetime
    start_hour: str
    end_hour: str
    min_participants: int = 2
    min_duration: int = 2
    max_duration: int = 4
    is_reminders_enabled: bool = False
    timezone: str = "Asia/Singapore"
    cancelled: bool = False
    creator: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class EventCreatePayload(SQLModel, table=False):
    event_id: str
    event_name: str
    event_description: str
    event_type: EventType = EventType.GENERAL
    start_date: str
    end_date: str
    start_hour: str
    end_hour: str
    creator: str
    is_reminders_enabled: bool = True
    cancelled: bool = False
    min_participants: int = 2
    min_duration: int = 2
    max_duration: int = 4
    timezone: str = "Asia/Singapore"


class ConfirmedEventRow(SQLModel, table=False):
    event_id: str
    confirmed_at: Optional[datetime] = None
    confirmed_start_time: str
    confirmed_end_time: str


class ConfirmedEventCreatePayload(SQLModel, table=False):
    event_id: str
    confirmed_at: str
    confirmed_start_time: str
    confirmed_end_time: str


class EventChatRow(SQLModel, table=False):
    event_id: str
    chat_id: int
    thread_id: Optional[int] = None


class EventChatCreatePayload(SQLModel, table=False):
    event_id: str
    chat_id: int
    thread_id: Optional[int] = None


class MembershipRow(SQLModel, table=False):
    user_uuid: str
    event_id: str
    joined_at: Optional[datetime] = None
    emoji_icon: Optional[str] = None


class AvailabilityBlockRow(SQLModel, table=False):
    event_id: str
    user_uuid: str
    start_time: str
    end_time: str


class UserRow(SQLModel, table=False):
    uuid: str
    tele_id: str
    tele_user: str = ""
    initialised: bool = False
    callout_cleared: bool = False
    sleep_start_time: Optional[str] = None
    sleep_end_time: Optional[str] = None
    tmp_sleep_start: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class UserCreatePayload(SQLModel, table=False):
    uuid: str
    tele_id: str
    tele_user: str = ""
    initialised: bool = False
    callout_cleared: bool = False
    sleep_start_time: Optional[str] = None
    sleep_end_time: Optional[str] = None
    created_at: str
    updated_at: str


class UserUpdatePayload(SQLModel, table=False):
    model_config = {"extra": "allow"}

    tele_user: Optional[str] = None
    initialised: Optional[bool] = None
    callout_cleared: Optional[bool] = None
    sleep_start_time: Optional[str] = None
    sleep_end_time: Optional[str] = None
    updated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class WebappShareTokenCreatePayload(SQLModel, table=False):
    token: str
    tele_id: str
    chat_id: int
    thread_id: Optional[int] = None
    message_id: int
    expires_at: str


class WebappShareTokenCtxRow(SQLModel, table=False):
    token: str
    tele_id: str
    chat_id: int
    thread_id: Optional[int] = None
    message_id: int
    expires_at: datetime
    used_at: Optional[datetime] = None


class EventMemberRow(SQLModel, table=False):
    user_uuid: str
    tele_id: str
    tele_user: str
    emoji_icon: Optional[str] = None
