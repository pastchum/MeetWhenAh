from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Import from best time algo
from best_time_algo.best_time_algo import BestTimeAlgo

# Import from services
from .database_service import getEntry, setEntry, getEntries, deleteEntries, setEntries, parse_row, parse_rows

# Import SQL models
from database.sqlmodels import (
    AvailabilityBlockRow,
    ConfirmedEventCreatePayload,
    ConfirmedEventRow,
    EventChatCreatePayload,
    EventChatRow,
    EventCreatePayload,
    EventRow,
    MembershipRow,
    UserRow,
)

# Import from utils
from utils.date_utils import parse_date, format_date_month_day, format_time_from_iso_am_pm

# Import from other
import uuid


def getEvent(event_id: str) -> Optional[Dict]:
    """Get event details by ID"""
    event = parse_row(getEntry("events", "event_id", event_id), EventRow)
    return event.model_dump(mode="json") if event else None


def create_event(event_name: str, event_description: str, start_date: str, end_date: str, creator_id: str, event_type: str = "general", start_hour: str = "00:00:00.000000+08:00", end_hour: str = "23:30:00.000000+08:00") -> Optional[str]:
    """Create a new event and return its ID"""
    event_id = str(uuid.uuid4())
    creator_details = parse_row(getEntry("users", "tele_id", creator_id), UserRow)
    if not creator_details:
        return None
    creator_uuid = creator_details.uuid
    event_data = EventCreatePayload(
        event_id=event_id,
        event_name=event_name,
        event_description=event_description,
        event_type=event_type,
        start_date=start_date,
        end_date=end_date,
        start_hour=start_hour,
        end_hour=end_hour,
        creator=creator_uuid,
        is_reminders_enabled=True,
        cancelled=False,
        min_participants=2,
        min_duration=2,
        max_duration=4,
        timezone="Asia/Singapore",
    )
    print(event_data)
    success = setEntry("events", event_id, event_data)
    print(success)
    return event_id if success else None


def get_event_chat(event_id: str) -> Optional[Tuple[int, int]]:
    """Get a chat for an event"""
    event_chats = getEntries("event_chats", "event_id", event_id)
    if not event_chats:
        return None
    event_chat = parse_row(event_chats[0], EventChatRow)
    if not event_chat:
        return None
    print("event_chat", event_chat)
    return event_chat.chat_id, event_chat.thread_id


def get_event_chats(event_id: str) -> List[Dict]:
    """Get all chats for an event"""
    chats = parse_rows(getEntries("event_chats", "event_id", event_id), EventChatRow)
    return [chat.model_dump(mode="json") for chat in chats]


def getEventSleepPreferences(event_id: str) -> Dict[str, Dict[str, int]]:
    """Get sleep preferences for all participants in an event"""
    event = parse_row(getEntry("events", "event_id", event_id), EventRow)
    if not event:
        return {}

    sleep_prefs = {}
    for user_id in event.model_dump(mode="json").get("participants", []):
        user = parse_row(getEntry("users", "uuid", user_id), UserRow)
        if user and user.sleep_start_time and user.sleep_end_time:
            sleep_prefs[user_id] = {
                "start": user.sleep_start_time,
                "end": user.sleep_end_time,
            }

    return sleep_prefs


def get_event_availability(event_id: str) -> List[Dict]:
    """Get all availability blocks for an event"""
    availability = parse_rows(getEntries("availability_blocks", "event_id", event_id), AvailabilityBlockRow)
    return [row.model_dump(mode="json") for row in availability]


def getUserAvailability(tele_id: str, event_id: str) -> List[Dict]:
    """Get a user's availability for an event"""
    availability = get_event_availability(event_id)
    if not availability:
        return []

    user_data = parse_row(getEntry("users", "tele_id", tele_id), UserRow)
    if not user_data:
        return []
    user_uuid = user_data.uuid
    if not user_uuid:
        return []

    availability_rows = parse_rows(availability, AvailabilityBlockRow)
    user_availability = [x for x in availability_rows if x.user_uuid == user_uuid]
    return [row.model_dump(mode="json") for row in user_availability]


def updateUserAvailability(tele_id: str, event_id: str, availability_data: List[Dict]) -> bool:
    """Update a user's availability for an event"""
    user_data = parse_row(getEntry("users", "tele_id", tele_id), UserRow)
    if not user_data:
        return False

    user_uuid = user_data.uuid
    if not user_uuid:
        return False

    # delete all availability blocks for the user for the event previously, if any
    successful_delete = deleteEntries("availability_blocks", "event_id", event_id, "user_uuid", [user_uuid])
    if not successful_delete:
        return False

    if not availability_data:  # no need to set if no availability data
        return True
    validated_blocks = [AvailabilityBlockRow.model_validate(block) for block in availability_data]
    successful_set = setEntries("availability_blocks", validated_blocks)
    if not successful_set:
        return False
    return True


def get_event_best_time(event_id: str) -> List[Dict]:
    """Get the best time for an event"""
    event = parse_row(getEntry("events", "event_id", event_id), EventRow)
    if not event:
        return []

    min_participants = event.min_participants
    min_duration_blocks = event.min_duration
    max_duration_blocks = event.max_duration

    best_time_algo = BestTimeAlgo(min_participants=min_participants, min_block_size=min_duration_blocks, max_block_size=max_duration_blocks)

    availability_blocks = get_event_availability(event_id)
    if not availability_blocks:
        return []

    best_event_blocks = best_time_algo._process_availability_blocks(availability_blocks)
    return best_event_blocks


def confirmEvent(event_id: str, best_start_time: str, best_end_time: str) -> bool:
    """Confirm an event"""
    event = parse_row(getEntry("events", "event_id", event_id), EventRow)
    if not event:
        return False

    confirmed_event_data = ConfirmedEventCreatePayload(
        event_id=event_id,
        confirmed_at=datetime.now(timezone.utc).isoformat(),
        confirmed_start_time=best_start_time,
        confirmed_end_time=best_end_time,
    )
    success = setEntry("confirmed_events", event_id, confirmed_event_data)
    if not success:
        return False
    return True


def getConfirmedEvent(event_id: str) -> Optional[Dict]:
    """Get a confirmed event"""
    event = parse_row(getEntry("confirmed_events", "event_id", event_id), ConfirmedEventRow)
    return event.model_dump(mode="json") if event else None


def generate_confirmed_event_description(event_id: str) -> str:
    """Generate a description for a confirmed event"""
    event_data = parse_row(getEvent(event_id), EventRow)
    confirmed_event_data = parse_row(getConfirmedEvent(event_id), ConfirmedEventRow)
    if not confirmed_event_data:
        return "Event not confirmed"
    description = ""
    if not event_data:
        return description
    description += f"\U0001f4c5 <b>Event</b>: <b>{event_data.event_name}</b>\n"
    description += f"\U0001f4dd <b>Description</b>: {event_data.event_description}\n"

    start_date = parse_date(confirmed_event_data.confirmed_start_time)
    start_date_str = format_date_month_day(start_date)
    start_time_str = format_time_from_iso_am_pm(confirmed_event_data.confirmed_start_time)

    end_date = parse_date(confirmed_event_data.confirmed_end_time)
    end_date_str = format_date_month_day(end_date)
    end_time_str = format_time_from_iso_am_pm(confirmed_event_data.confirmed_end_time)

    description += f"\u23f0 <b>Duration</b>: {start_date_str} {start_time_str} to {end_date_str} {end_time_str}\n"
    return description


def generate_confirmed_event_participants_list(event_id: str) -> str:
    """Generate a list for the participants of a confirmed event"""
    description = ""
    participants = getEntries("membership", "event_id", event_id)
    if not participants:
        return description
    participant_rows = parse_rows(participants, MembershipRow)
    for participant in participant_rows:
        user_data = parse_row(getEntry("users", "uuid", participant.user_uuid), UserRow)
        if user_data:
            description += f"@{user_data.tele_user}\n"
    return description


def generate_event_description(event: dict) -> str:
    """Generate a description for an event"""
    parsed_event = parse_row(event, EventRow)
    description = ""
    if not parsed_event:
        return description

    if parsed_event.event_name:
        description += f"\U0001f4c5 <b>Event</b>: <b>{parsed_event.event_name}</b>\n"

    if parsed_event.event_description:
        desc = parsed_event.event_description
        if len(parsed_event.event_description) > 50:
            desc = parsed_event.event_description[:47] + "..."
        description += f"\U0001f4dd <b>Description</b>: {desc}\n"

    if parsed_event.start_date and parsed_event.end_date:
        start_date = parse_date(str(parsed_event.start_date))
        end_date = parse_date(str(parsed_event.end_date))
        start_date_str = format_date_month_day(start_date)
        end_date_str = format_date_month_day(end_date)
        description += f"\u23f0 <b>Date Range</b>: {start_date_str} - {end_date_str}\n"

    return description


def generate_confirmed_event_markup(event_id: str) -> InlineKeyboardMarkup:
    """Generate a markup for a confirmed event"""
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Join Event", callback_data=f"join_event_{event_id}"))
    return markup


if __name__ == "__main__":
    event_id = "44e211d3-a094-4133-9ea0-4539c091c07c"
    event = getEvent(event_id)
    print(event)

    best_time = get_event_best_time(event_id)
    print(best_time)
