"""Membership operations — join, leave, and check membership for events."""

from datetime import datetime, timezone

from .database_service import getEntry, getEntries, setEntry, deleteEntry, parse_row, parse_rows
from database.sqlmodels import ConfirmedEventRow, EventRow, MembershipRow, UserRow


def join_event_by_uuid(event_id: str, user_uuid: str) -> bool:
    """Add a user to an event's membership by UUID"""
    confirmed = parse_row(getEntry("confirmed_events", "event_id", event_id), ConfirmedEventRow)
    if not confirmed:
        return False

    membership_data = MembershipRow(
        event_id=event_id,
        user_uuid=user_uuid,
        joined_at=datetime.now(timezone.utc),
        emoji_icon="👋",
    )
    return setEntry("membership", event_id, membership_data)


def join_event(event_id: str, tele_id: str) -> bool:
    """Add a user to an event's membership by tele_id"""
    confirmed = parse_row(getEntry("confirmed_events", "event_id", event_id), ConfirmedEventRow)
    if not confirmed:
        return False

    user = parse_row(getEntry("users", "tele_id", str(tele_id)), UserRow)
    if not user:
        return False

    return join_event_by_uuid(event_id, user.uuid)


def leave_event(event_id: str, tele_id: str) -> bool:
    """Remove a user from an event's membership"""
    confirmed = parse_row(getEntry("confirmed_events", "event_id", event_id), ConfirmedEventRow)
    if not confirmed:
        return False

    user = parse_row(getEntry("users", "tele_id", str(tele_id)), UserRow)
    if not user:
        return False

    return deleteEntry("membership", "event_id", event_id, "user_uuid", user.uuid)


def check_membership(event_id: str, tele_id: str) -> bool:
    """Check if a user is a member of an event"""
    confirmed = parse_row(getEntry("confirmed_events", "event_id", event_id), ConfirmedEventRow)
    if not confirmed:
        return False

    user = parse_row(getEntry("users", "tele_id", str(tele_id)), UserRow)
    if not user:
        return False

    members = getEntries("membership", "event_id", event_id)
    if not members:
        return False

    member_rows = parse_rows(members, MembershipRow)
    return any(m.user_uuid == user.uuid for m in member_rows)


def check_ownership(event_id: str, tele_id: str) -> bool:
    """Check if a user is the creator of an event"""
    event = parse_row(getEntry("events", "event_id", event_id), EventRow)
    if not event:
        return False

    user = parse_row(getEntry("users", "tele_id", str(tele_id)), UserRow)
    if not user:
        return False

    return event.creator == user.uuid
