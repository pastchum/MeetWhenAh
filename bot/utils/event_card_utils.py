from datetime import datetime
from utils.date_utils import parse_date, format_date, format_date_for_message


def generate_event_card_text(e: dict) -> str:
    start = format_date_for_message(parse_date(e.get("start_date") or e.get("start_time") or ""))
    end   = format_date_for_message(parse_date(e.get("end_date")   or e.get("end_time")   or ""))
    desc  = (e.get("description") or "").strip()
    #TODO: Add event type to the event card
    parts = [
        f"<b>{e.get('event_name','Untitled Event')}</b>",   
        f"{desc}" if desc else "",
        f"🗓 <b>Window:</b> {start} → {end}" if start or end else "",
        f"ID: <code>{e.get('event_id')}</code>" if e.get("event_id") else ""
    ]
    return "\n".join([p for p in parts if p])