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
from utils.date_utils import format_date_for_message, format_time_from_iso, parse_date, parse_time, format_time, format_date_month_day, format_time_from_iso_am_pm

# Import from other
import uuid

import events.confirmed_events as confirmed_events

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
        self.event_id = event_id
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
    def _create_event(self, 
                 event_name: str, event_description: str, event_type: str, start_date: str, end_date: str, start_hour: str, end_hour: str, creator: str):
        self.event_id = str(uuid.uuid4())
        event_data = {
            "event_id": self.event_id,
            "event_name": event_name,
            "event_description": event_description,
            "event_type": event_type,
            "start_date": start_date,
            "end_date": end_date,
            "start_hour": start_hour,
            "end_hour": end_hour,
            "creator": creator,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }

        success = setEntry("events", self.event_id, event_data)
        if not success:
            return None

        return self
    
    """
    Confirm an event in database
    """
    def _confirm_event(self, best_start_time: str, best_end_time: str):
        now = datetime.now(timezone.utc).isoformat()
        confirmed_event_data = {
            "event_id": self.event_id,
            "confirmed_at": now,
            "confirmed_start_time": best_start_time,
            "confirmed_end_time": best_end_time
        }
        success = setEntry("confirmed_events", self.event_id, confirmed_event_data)
        if not success:
            raise Exception("Failed to confirm event")
        confirmed_event = confirmed_events.ConfirmedEvent.from_event(self, 
                                                                     now, 
                                                                     best_start_time, 
                                                                     best_end_time)
        return confirmed_event

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
    def get_event_from_database(self, event_id: str) -> Optional[Dict]:
        event = getEntry("events", "event_id", event_id)
        return event if event else None
    
    """
    Create event in database
    """
    def create_event(self, event_name: str, event_description: str, event_type: str, start_date: str, end_date: str, start_hour: str, end_hour: str, creator: str):
        return self._create_event(event_name, event_description, event_type, start_date, end_date, start_hour, end_hour, creator)
    
    """
    Confirm an event
    """
    def confirm_event(self, best_start_time: str, best_end_time: str):
        return self._confirm_event(best_start_time, best_end_time)

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