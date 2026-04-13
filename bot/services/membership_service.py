"""Membership operations — join, leave, and check membership for events."""

from datetime import datetime, timezone

from .database_service import getEntry, getEntries, setEntry, deleteEntry


def join_event_by_uuid(event_id: str, user_uuid: str) -> bool:
    """Add a user to an event's membership by UUID"""
    confirmed = getEntry("confirmed_events", "event_id", event_id)
    if not confirmed:
        return False

    membership_data = {
        "event_id": event_id,
        "user_uuid": user_uuid,
        "joined_at": datetime.now(timezone.utc).isoformat(),
        "emoji_icon": "👋",
    }
    return setEntry("membership", event_id, membership_data)


def join_event(event_id: str, tele_id: str) -> bool:
    """Add a user to an event's membership by tele_id"""
    confirmed = getEntry("confirmed_events", "event_id", event_id)
    if not confirmed:
        return False

    user = getEntry("users", "tele_id", str(tele_id))
    if not user:
        return False

    return join_event_by_uuid(event_id, user["uuid"])


def leave_event(event_id: str, tele_id: str) -> bool:
    """Remove a user from an event's membership"""
    confirmed = getEntry("confirmed_events", "event_id", event_id)
    if not confirmed:
        return False

    user = getEntry("users", "tele_id", str(tele_id))
    if not user:
        return False

    return deleteEntry("membership", "event_id", event_id, "user_uuid", user["uuid"])


def check_membership(event_id: str, tele_id: str) -> bool:
    """Check if a user is a member of an event"""
    confirmed = getEntry("confirmed_events", "event_id", event_id)
    if not confirmed:
        return False

    user = getEntry("users", "tele_id", str(tele_id))
    if not user:
        return False

    members = getEntries("membership", "event_id", event_id)
    if not members:
        return False

    return any(m["user_uuid"] == user["uuid"] for m in members)


def check_ownership(event_id: str, tele_id: str) -> bool:
    """Check if a user is the creator of an event"""
    event = getEntry("events", "event_id", event_id)
    if not event:
        return False

    user = getEntry("users", "tele_id", str(tele_id))
    if not user:
        return False

    return event["creator"] == user["uuid"]
