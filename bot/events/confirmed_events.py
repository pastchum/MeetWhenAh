from datetime import datetime, timezone
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


# Import from services
from services.database_service import getEntry, setEntry, getEntries, deleteEntry, supabase

# Import from utils
from utils.date_utils import parse_date, format_date_month_day, format_time_from_iso_am_pm
from utils.overrides_utils import overrides

# Import from other
import uuid

from events.events import Event

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

class ConfirmedEvent(Event):
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
                 confirmed_start_time: str, 
                 confirmed_end_time: str,
                 confirmed_at: str, 
                 min_participants: int = 2, 
                 min_duration: int = 2, 
                 max_duration: int = 4, 
                 is_reminders_enabled: bool = True, 
                 timezone: str = "Asia/Singapore", ):
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

    """
    Create confirmed event in database
    """
    @classmethod
    def from_event(cls, event: Event, confirmed_at: str, confirmed_start_time: str, confirmed_end_time: str):
        confirmed_event = cls(event_id = event.event_id,
                             event_name = event.event_name,
                             event_description = event.event_description,
                             event_type = event.event_type,
                             start_date = event.start_date,
                             end_date = event.end_date,
                             start_hour = event.start_hour, 
                             end_hour = event.end_hour, 
                             creator = event.creator, 
                             created_at = event.created_at, 
                             updated_at = event.updated_at, 
                             min_participants = event.min_participants, 
                             min_duration = event.min_duration, 
                             max_duration = event.max_duration, 
                             is_reminders_enabled = event.is_reminders_enabled, 
                             timezone = event.timezone, 
                             confirmed_at = confirmed_at, 
                             confirmed_start_time = confirmed_start_time, 
                             confirmed_end_time = confirmed_end_time)
        
        confirmed_event_data = {
            "event_id": event.event_id,
            "confirmed_at": confirmed_event.confirmed_at,
            "confirmed_start_time": confirmed_event.confirmed_start_time,
            "confirmed_end_time": confirmed_event.confirmed_end_time
        }
        isConfirmed = getEntry("confirmed_events", "event_id", event.event_id)
        if not isConfirmed:
            isConfirmed = setEntry("confirmed_events", event.event_id, confirmed_event_data)
        
        if not isConfirmed:
            raise Exception("Failed to confirm event")
        
        return confirmed_event
    
    @classmethod
    def from_database(cls, event_id: str):
        event = Event.from_database(event_id)
        if not event:
            return None
        confirmed_event = getEntry("confirmed_events", "event_id", event_id)
        if not confirmed_event:
            return None
        return ConfirmedEvent.from_event(event, confirmed_event.get("confirmed_at"), confirmed_event.get("confirmed_start_time"), confirmed_event.get("confirmed_end_time"))

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
        response = supabase.rpc("get_event_members", { "p_event_id": self.event_id }).execute()
        return response.data

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
    @overrides(Event)
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

    @overrides(Event)
    def _get_event_button(self):
        markup = InlineKeyboardMarkup()
        # override to add join event
        markup.add(InlineKeyboardButton("Join Event", callback_data=f"join:{self.event_id}"))
        return markup

    @overrides(Event)
    def get_event_details_for_message(self):
        return self._get_event_details_for_message()
    
    @overrides(Event)
    def get_event_button(self):
        return self._get_event_button()