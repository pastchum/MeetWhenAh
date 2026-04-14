"""SQLAlchemy ORM models for MeetWhenAh database."""

import enum
import uuid

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    Enum,
    ForeignKey,
    Index,
    Integer,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.types import DateTime, Time


class TimingEnum(enum.Enum):
    MORNING = "MORNING"
    AFTERNOON = "AFTERNOON"
    NIGHT = "NIGHT"


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tele_id = Column(BigInteger, unique=True)
    tele_user = Column(Text, unique=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default="now()")
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default="now()")
    initialised = Column(Boolean, default=False)
    callout_cleared = Column(Boolean, default=False)
    sleep_start_time = Column(Time(timezone=True))
    sleep_end_time = Column(Time(timezone=True))
    tmp_sleep_start = Column(Time(timezone=True))

    # Relationships
    created_events = relationship("Event", back_populates="creator_user")
    memberships = relationship("Membership", back_populates="user")
    availability_blocks = relationship("AvailabilityBlock", back_populates="user")
    blocked_timings = relationship("BlockedTiming", back_populates="user")
    share_tokens = relationship("WebappShareToken", back_populates="user")


class Event(Base):
    __tablename__ = "events"

    event_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_name = Column(Text, nullable=False)
    event_description = Column(Text, nullable=False)
    event_type = Column(Text, nullable=False)
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    start_hour = Column(
        Time(timezone=True), nullable=False, server_default="'00:00:00+08:00'"
    )
    end_hour = Column(
        Time(timezone=True), nullable=False, server_default="'23:30:00+08:00'"
    )
    min_participants = Column(Integer, nullable=False, server_default="2")
    min_duration = Column(Integer, nullable=False, server_default="2")
    max_duration = Column(Integer, nullable=False, server_default="4")
    is_reminders_enabled = Column(Boolean, nullable=False, server_default="false")
    timezone = Column(Text, nullable=False, server_default="'Asia/Singapore'")
    cancelled = Column(Boolean, nullable=False, server_default="false")
    creator = Column(
        UUID(as_uuid=True),
        ForeignKey("users.uuid", ondelete="RESTRICT"),
        nullable=False,
    )
    created_at = Column(DateTime(timezone=True), nullable=False, server_default="now()")

    # Relationships
    creator_user = relationship("User", back_populates="created_events")
    confirmed_event = relationship(
        "ConfirmedEvent", back_populates="event", uselist=False
    )
    event_chats = relationship("EventChat", back_populates="event")
    memberships = relationship("Membership", back_populates="event")
    availability_blocks = relationship("AvailabilityBlock", back_populates="event")

    __table_args__ = (Index("idx_events_creator", "creator"),)


class ConfirmedEvent(Base):
    __tablename__ = "confirmed_events"

    event_id = Column(
        UUID(as_uuid=True),
        ForeignKey("events.event_id", ondelete="CASCADE"),
        primary_key=True,
    )
    confirmed_at = Column(
        DateTime(timezone=True), nullable=False, server_default="now()"
    )
    confirmed_start_time = Column(DateTime(timezone=True))
    confirmed_end_time = Column(DateTime(timezone=True))

    # Relationships
    event = relationship("Event", back_populates="confirmed_event")


class EventChat(Base):
    __tablename__ = "event_chats"

    event_id = Column(
        UUID(as_uuid=True),
        ForeignKey("events.event_id", ondelete="CASCADE"),
        primary_key=True,
    )
    chat_id = Column(BigInteger, primary_key=True)
    thread_id = Column(BigInteger)

    # Relationships
    event = relationship("Event", back_populates="event_chats")


class Membership(Base):
    __tablename__ = "membership"

    user_uuid = Column(
        UUID(as_uuid=True),
        ForeignKey("users.uuid", ondelete="CASCADE"),
        primary_key=True,
    )
    event_id = Column(
        UUID(as_uuid=True),
        ForeignKey("events.event_id", ondelete="CASCADE"),
        primary_key=True,
    )
    joined_at = Column(DateTime(timezone=True), nullable=False, server_default="now()")
    emoji_icon = Column(Text, nullable=False)

    # Relationships
    user = relationship("User", back_populates="memberships")
    event = relationship("Event", back_populates="memberships")

    __table_args__ = (
        Index("idx_membership_event_id", "event_id"),
        Index("idx_membership_user_uuid", "user_uuid"),
    )


class AvailabilityBlock(Base):
    __tablename__ = "availability_blocks"

    event_id = Column(
        UUID(as_uuid=True),
        ForeignKey("events.event_id", ondelete="CASCADE"),
        primary_key=True,
    )
    user_uuid = Column(
        UUID(as_uuid=True),
        ForeignKey("users.uuid", ondelete="CASCADE"),
        primary_key=True,
    )
    start_time = Column(DateTime(timezone=True), primary_key=True, nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)

    # Relationships
    event = relationship("Event", back_populates="availability_blocks")
    user = relationship("User", back_populates="availability_blocks")

    __table_args__ = (
        Index("idx_availability_blocks_event_id", "event_id"),
        Index("idx_availability_blocks_user_uuid", "user_uuid"),
        Index("idx_availability_blocks_start_time", "start_time"),
    )


class BlockedTiming(Base):
    __tablename__ = "blocked_timings"

    uuid = Column(
        UUID(as_uuid=True),
        ForeignKey("users.uuid", ondelete="CASCADE"),
        primary_key=True,
    )
    start_time = Column(DateTime(timezone=True), primary_key=True, nullable=False)
    end_time = Column(DateTime(timezone=True), primary_key=True, nullable=False)

    # Relationships
    user = relationship("User", back_populates="blocked_timings")

    __table_args__ = (Index("idx_blocked_timings_uuid", "uuid"),)


class WebappShareToken(Base):
    __tablename__ = "webapp_share_tokens"

    token = Column(Text, primary_key=True)
    tele_id = Column(BigInteger, ForeignKey("users.tele_id"), nullable=False)
    chat_id = Column(BigInteger, nullable=False)
    thread_id = Column(BigInteger)
    message_id = Column(BigInteger, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default="now()")
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used_at = Column(DateTime(timezone=True))

    # Relationships
    user = relationship("User", back_populates="share_tokens")

    __table_args__ = (
        Index("idx_share_tokens_expires", "expires_at"),
        Index("idx_share_tokens_user", "tele_id"),
    )
