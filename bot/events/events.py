from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Import from config
from telegram.config.config import bot

# Import from best time algo
from best_time_algo.best_time_algo import BestTimeAlgo

# Import from services
from services.database_service import getEntry, setEntry, getEntries

# Import from utils
from utils.date_utils import parse_date, format_date_month_day

# Import from other
import uuid

"""
Event class with methods and fields for handling events

Database schema for reference:
  event_id        UUID            PRIMARY KEY,
  event_name      TEXT    NOT NULL,
  event_description TEXT    NOT NULL,    
  event_type      TEXT    NOT NULL,
  start_date      TIMESTAMPTZ       NOT NULL,      
  end_date        TIMESTAMPTZ       NOT NULL,      
  start_hour     TIMETZ         NOT NULL DEFAULT '00:00:00.000000+08:00',
  end_hour       TIMETZ         NOT NULL DEFAULT '23:30:00.000000+08:00',
  min_participants INT NOT NULL DEFAULT 2,
  min_duration INT NOT NULL DEFAULT 2, -- in terms of blocks
  max_duration INT NOT NULL DEFAULT 4, -- in terms of blocks
  is_reminders_enabled BOOLEAN NOT NULL DEFAULT false,
  timezone TEXT NOT NULL DEFAULT 'Asia/Singapore',
  creator         UUID            NOT NULL
                    REFERENCES users(uuid)
                    ON DELETE RESTRICT,
  created_at      TIMESTAMPTZ       NOT NULL DEFAULT NOW()
"""
class Event:
    def __init__(self, 
                 event_id: str, 
                 event_name: str, 
                 event_description: str, 
                 event_type: str, 
                 start_date: str, 
                 end_date: str, 
                 start_hour: str, 
                 end_hour: str, 
                 creator: str, 
                 created_at: str, 
                 updated_at: str, 
                 min_participants: int, 
                 min_duration: int, 
                 max_duration: int, 
                 is_reminders_enabled: bool, 
                 timezone: str):
        self.event_id = event_id if event_id else str(uuid.uuid4())
        self.event_name = event_name
        self.event_description = event_description
        self.event_type = event_type
        self.start_date = start_date
        self.end_date = end_date
        self.start_hour = start_hour
        self.end_hour = end_hour
        self.creator = creator
        self.created_at = created_at
        self.updated_at = updated_at
        self.min_participants = min_participants
        self.min_duration = min_duration
        self.max_duration = max_duration
        self.is_reminders_enabled = is_reminders_enabled
        self.timezone = timezone

    def get_event_id(self) -> str:
        return self.event_id

    def get_event_name(self) -> str:
        return self.event_name
        

    """
    Get Event field methods
    """
    def get_event_description(self) -> str:
        return self.event_description
        
    def get_event_type(self) -> str:
        return self.event_type

    def get_start_date(self) -> str:
        return self.start_date

    def get_end_date(self) -> str:
        return self.end_date

    def get_start_hour(self) -> str:
        return self.start_hour

    def get_end_hour(self) -> str:
        return self.end_hour

    def get_creator(self) -> str:
        return self.creator
        
    def get_created_at(self) -> str:
        return self.created_at

    def get_updated_at(self) -> str:
        return self.updated_at

    def get_min_participants(self) -> int:
        return self.min_participants
        
    def get_min_duration(self) -> int:
        return self.min_duration

    def get_max_duration(self) -> int:
        return self.max_duration

    def get_is_reminders_enabled(self) -> bool:
        return self.is_reminders_enabled

    def get_timezone(self) -> str:
        return self.timezone

    """
    Create event in database
    """
    def _create_event( 
                 event_name: str, 
                 event_description: str, 
                 event_type: str, 
                 start_date: str, 
                 end_date: str, 
                 start_hour: str, 
                 end_hour: str, 
                 creator: str, 
                 created_at: str, 
                 updated_at: str, 
                 min_participants: int, 
                 min_duration: int, 
                 max_duration: int, 
                 is_reminders_enabled: bool, 
                 timezone: str, 
                 event_id: str):
        event = Event(event_id, 
            event_name, 
            event_description, 
            event_type, 
            start_date, 
            end_date, 
            start_hour, 
            end_hour, 
            creator, 
            created_at, 
            updated_at, 
            min_participants, 
            min_duration, 
            max_duration, 
            is_reminders_enabled, 
            timezone)
        
        event_data = {
            "event_id": event_id,
            "event_name": event_name,
            "event_description": event_description,
            "event_type": event_type,
            "start_date": start_date,
            "end_date": end_date,
            "start_hour": start_hour,
            "end_hour": end_hour,
            "creator": creator,
            "created_at": created_at,
            "updated_at": updated_at,
            "min_participants": min_participants,
            "min_duration": min_duration,
            "max_duration": max_duration,
            "is_reminders_enabled": is_reminders_enabled,
            "timezone": timezone
        }

        success = setEntry("events", event_id, event_data)
        if not success:
            return None

        return event

    """
    Get all chats from chat table for given event
    """
    def _get_chats_for_event(self):
        return getEntries("event_chats", "event_id", self.event_id)
    
    """
    Get all event availabilities
    """
    def _get_availability_blocks_for_event(self):
        return getEntries("availability_blocks", "event_id", self.event_id)
    
    """
    Get best time for event
    """
    def _get_best_time_for_event(self):
        best_time_algo = BestTimeAlgo(min_participants=self.min_participants, min_block_size=self.min_duration, max_block_size=self.max_duration)
        availability_blocks = self._get_availability_blocks_for_event()
        if not availability_blocks:
            return None
        best_time_algo._process_availability_blocks(availability_blocks)
        return best_time_algo._get_best_event_block(availability_blocks)

    """
    Get event from database
    """
    @classmethod
    def from_database(cls, event_id: str) -> Optional['Event']:
        event = getEntry("events", "event_id", event_id)
        if not event:
            return None
        return cls(
            event_id=event.get("event_id"),
            event_name=event.get("event_name"),
            event_description=event.get("event_description"),
            event_type=event.get("event_type"),
            start_date=event.get("start_date"),
            end_date=event.get("end_date"),
            start_hour=event.get("start_hour"),
            end_hour=event.get("end_hour"),
            creator=event.get("creator"),
            created_at=event.get("created_at"),
            updated_at=event.get("updated_at"),
            min_participants=event.get("min_participants"),
            min_duration=event.get("min_duration"),
            max_duration=event.get("max_duration"),
            is_reminders_enabled=event.get("is_reminders_enabled"),
            timezone=event.get("timezone")
        )
    
    """
    Create event in database
    """
    def create_event(event_name: str, 
                event_description: str, 
                event_type: str, 
                start_date: str, 
                end_date: str, 
                start_hour: str, 
                end_hour: str, 
                creator: str,
                min_participants: int = 2,
                min_duration: int = 2,
                max_duration: int = 4,
                is_reminders_enabled: bool = False,
                timezone: str = "Asia/Singapore",
                event_id: str = None):
        created_at = datetime.now(timezone.utc).isoformat()
        updated_at = datetime.now(timezone.utc).isoformat()
        event_id_to_use = event_id if event_id else str(uuid.uuid4())
        return Event._create_event(event_name, 
                            event_description, 
                            event_type, 
                            start_date, 
                            end_date, 
                            start_hour, 
                            end_hour, 
                            creator,
                            created_at,
                            updated_at,
                            min_participants,
                            min_duration,
                            max_duration,
                            is_reminders_enabled,
                            timezone,
                            event_id_to_use)

    """
    Get best time for an
    """
    def get_best_time_for_event(self):
        return self._get_best_time_for_event()
    
    """
    Get all chats for event
    """
    def get_chats_for_event(self):
        return self._get_chats_for_event()
    
    """
    Get all availability blocks for event
    """
    def get_availability_blocks_for_event(self):
        return self._get_availability_blocks_for_event()
    
    """
    format event details for message
    """
    def _get_event_details_for_message(self):
        description = ""
        # Event name
        if self.event_name:
            description += f"📅 <b>Event</b>: <b>{self.event_name}</b>\n"
        
        # Event description (truncated to one line)
        if self.event_description:
            desc = self.event_description
            # Truncate to one line and add dots if needed
            if len(desc) > 50:
                desc = desc[:47] + "..."
            description += f"📝 <b>Description</b>: {desc}\n"
        
        # Date range
        if self.start_date and self.end_date:
            start_date = parse_date(self.start_date)
            end_date = parse_date(self.end_date)
            start_date_str = format_date_month_day(start_date)
            end_date_str = format_date_month_day(end_date)
            description += f"📅 <b>Date Range</b>: {start_date_str} - {end_date_str}\n"
        
        return description
    
    """
    format event details for button
    """
    def _get_event_button(self):
        markup = InlineKeyboardMarkup()
        # add select availability button

        params = f"dragselector={self.event_id}"
        miniapp_url = f"https://t.me/{bot.get_me().username}/meetwhenah?startapp={params}"

        markup.add(InlineKeyboardButton("Select Availability", url=miniapp_url))
        return markup

    """
    Methods for displaying event details
    """
    def get_event_details_for_message(self):
        return self._get_event_details_for_message()
    
    def get_event_button(self):
        return self._get_event_button()