from datetime import datetime, timedelta
from typing import Generator

def daterange(start_date: datetime, end_date: datetime) -> Generator[datetime, None, None]:
    """Generate a range of dates between start_date and end_date (inclusive)"""
    for n in range(int((end_date - start_date).days) + 1):
        yield start_date + timedelta(n)

def format_date(date: datetime) -> str:
    """Format a date object to string in YYYY-MM-DD format"""
    return date.strftime("%Y-%m-%d")

def parse_date(date_str: str) -> datetime:
    """Parse a date string in YYYY-MM-DD format to datetime object"""
    return datetime.strptime(date_str, "%Y-%m-%d")

def format_time(time: int) -> str:
    """Format a time integer (HHMM) to string (HH:MM)"""
    hours = time // 100
    minutes = time % 100
    return f"{hours:02d}:{minutes:02d}"

def parse_time(time_str: str) -> int:
    """Parse a time string (HH:MM) to integer (HHMM)"""
    hours, minutes = map(int, time_str.split(":"))
    return hours * 100 + minutes 