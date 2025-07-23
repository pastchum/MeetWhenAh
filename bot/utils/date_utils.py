from datetime import datetime, timedelta, timezone
from typing import Generator

def daterange(start_date: datetime, end_date: datetime) -> Generator[datetime, None, None]:
    """Generate a range of dates between start_date and end_date (inclusive)"""
    for n in range(int((end_date - start_date).days) + 1):
        yield start_date + timedelta(n)

def format_date(date: datetime) -> str:
    """Format a date object to string in YYYY-MM-DD format"""
    if date.tzinfo is None:
        # If no timezone info, assume UTC
        date = date.replace(tzinfo=timezone.utc)
    return date.isoformat()

def parse_date(datetime_str: str) -> datetime:
    """Parse a date string in YYYY-MM-DD format to datetime object"""
    try:
        return datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
    except ValueError:
        pass
        
    # Try strptime with timezone format
    try:
        return datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M:%S%z")
    except ValueError:
        pass
        
    # Try the old format as fallback (timezone-naive, assume UTC)
    try:
        dt = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
        return dt.replace(tzinfo=timezone.utc)
    except ValueError:
        pass
        
    # Try ISO format without timezone (assume UTC)
    try:
        dt = datetime.fromisoformat(datetime_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except ValueError:
        pass
        
        # If all else fails, raise an error
    raise ValueError(f"Unable to parse datetime string: {datetime_str}")

def format_date_for_message(date: datetime) -> str:
    """Format a date object to string in YYYY-MM-DD format"""
    return date.strftime("%Y-%m-%d")

def format_time(time: int) -> str:
    """Format a time integer (HHMM) to string (HH:MM)"""
    hours = time // 100
    minutes = time % 100
    return f"{hours:02d}:{minutes:02d}"

def format_time_from_iso(datetime_str: str) -> str:
    """Format a datetime string in ISO format to string in HH:MM format"""
    date = parse_date(datetime_str)
    return date.strftime("%H:%M")

def parse_time(time_str: str) -> int:
    """Parse a time string in the form of HH:mm:ss+tz to integer (HHMM)"""
    # Remove timezone if present
    if "+" in time_str:
        time_str = time_str.split("+")[0]
    elif "-" in time_str and time_str.count(":") > 2:
        # Handle negative timezone (e.g., 12:30:00-05:00)
        time_str = time_str.rsplit("-", 1)[0]
    # Remove seconds if present
    parts = time_str.split(":")
    hours = int(parts[0])
    minutes = int(parts[1]) if len(parts) > 1 else 0
    return hours * 100 + minutes
    