from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Import from best time algo
from best_time_algo.best_time_algo import BestTimeAlgo

# Import from services
from services.database_service import getEntry, setEntry, updateEntry, getEntries, deleteEntries, setEntries, deleteEntry

# Import from utils
from utils.date_utils import format_date_for_message, format_time_from_iso, parse_date, parse_time, format_time, format_date_month_day, format_time_from_iso_am_pm
from utils.overrides_utils import overrides

# Import from other
import uuid

import events.events as events

"""
Class for confirmed events, inherits from Event class

Database Scehema for reference
  event_id        UUID            NOT NULL
                    REFERENCES events(event_id)
                    ON DELETE CASCADE,
  confirmed_at      TIMESTAMPTZ       NOT NULL DEFAULT NOW(),
  confirmed_start_time TIMESTAMPTZ,
  confirmed_end_time TIMESTAMPTZ,
"""

class ConfirmedEvent(events.Event):
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
                 timezone: str, 
                 confirmed_at: str, 
                 confirmed_start_time: str, 
                 confirmed_end_time: str):
        super().__init__(event_id, 
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
        self.confirmed_at = confirmed_at
        self.confirmed_start_time = confirmed_start_time
        self.confirmed_end_time = confirmed_end_time

    def from_event(self, event: events.Event, confirmed_at: str, confirmed_start_time: str, confirmed_end_time: str):
        return self.__init__(event.event_id,
                             event.event_name,
                             event.event_description,
                             event.event_type,
                             event.start_date,
                             event.end_date,
                             event.start_hour, 
                             event.end_hour, 
                             event.creator, 
                             event.created_at, 
                             event.updated_at, 
                             event.min_participants, 
                             event.min_duration, 
                             event.max_duration, 
                             event.is_reminders_enabled, 
                             event.timezone, 
                             confirmed_at, 
                             confirmed_start_time, 
                             confirmed_end_time)

    """
    field methods
    """
    def get_confirmed_at(self) -> str:
        return self.confirmed_at
    
    def get_confirmed_start_time(self) -> str:
        return self.confirmed_start_time
    
    def get_confirmed_end_time(self) -> str:
        return self.confirmed_end_time
    
    """
    Handle user joining event
    """

    """
    Add user to membership table for given event
    """
    def _add_user_to_event(self, user_uuid: str):
        membership_data = {
        "event_id": self.event_id,
        "user_uuid": user_uuid,
        "joined_at": datetime.now(timezone.utc).isoformat(),
        "emoji_icon": "👋"
        }
        success = setEntry("membership", self.event_id, membership_data)
        if not success:
            return False
        return True
    
    """
    Remove user from membership table for given event
    """
    def _remove_user_from_event(self, user_uuid: str):
        success = deleteEntry("membership", "event_id", self.event_id, "user_uuid", user_uuid)
        if not success:
            return False
        return True
    
    """
    Get all users from membership table for given event
    """
    def _get_all_users_for_event(self):
        return getEntries("membership", "event_id", self.event_id)

    """
    Add user to event
    """
    def add_user_to_event(self, user_uuid: str):
        return self._add_user_to_event(user_uuid)
    
    """
    Remove user from event
    """
    def remove_user_from_event(self, user_uuid: str):
        return self._remove_user_from_event(user_uuid)
    
    """
    Get all users for event
    """
    def get_all_users_for_event(self):
        return self._get_all_users_for_event()
    

    """
    Display overrides
    """
    @overrides(events.Event._get_event_details_for_message)
    def _get_event_details_for_message(self):
            description = ""

            # add event name and description
            description += f"📅 <b>Event</b>: <b>{self.event_name}</b>\n"
            description += f"📝 <b>Description</b>: {self.event_description}\n"

            # parse start time
            start_date = parse_date(self.confirmed_start_time)
            start_date_str = format_date_month_day(start_date)
            start_time_str = format_time_from_iso_am_pm(self.confirmed_start_time)

            # parse end time
            end_date = parse_date(self.confirmed_end_time)
            end_date_str = format_date_month_day(end_date)
            end_time_str = format_time_from_iso_am_pm(self.confirmed_end_time)

            # add start and end time
            description += f"⏰ <b>Duration</b>: {start_date_str} {start_time_str} to {end_date_str} {end_time_str}\n"

            return description

    @overrides(events.Event._get_event_button)
    def _get_event_button(self):
        markup = InlineKeyboardMarkup()
        # override to add join event
        markup.add(InlineKeyboardButton("Join Event", callback_data=f"join_event_{self.event_id}"))
        return markup

    @overrides(events.Event.get_event_details_for_message)
    def get_event_details_for_message(self):
        return super()._get_event_details_for_message()
    
    @overrides(events.Event.get_event_button)
    def get_event_button(self):
        return self._get_event_button()