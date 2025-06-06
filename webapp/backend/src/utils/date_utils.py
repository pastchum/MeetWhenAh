from datetime import datetime, timedelta

def daterange(start_date, end_date):
    """
    Generator function to iterate through dates between start_date and end_date.
    
    Args:
        start_date (datetime): The start date.
        end_date (datetime): The end date.
        
    Yields:
        datetime: Each date between start_date and end_date.
    """
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)

def format_time(time_str):
    """
    Format a time string from HHMM format to HH:MM format.
    
    Args:
        time_str (str): Time string in HHMM format.
        
    Returns:
        str: Time string in HH:MM format.
    """
    if len(time_str) != 4:
        return time_str
    return f"{time_str[:2]}:{time_str[2:]}"

def parse_time(time_str):
    """
    Parse a time string in HHMM format to hours and minutes.
    
    Args:
        time_str (str): Time string in HHMM format.
        
    Returns:
        tuple: A tuple of (hours, minutes).
    """
    try:
        hours = int(time_str[:2])
        minutes = int(time_str[2:])
        return hours, minutes
    except (ValueError, IndexError):
        return None, None

def is_valid_time(time_str):
    """
    Check if a time string is valid (HHMM format, 24-hour).
    
    Args:
        time_str (str): Time string to validate.
        
    Returns:
        bool: True if valid, False otherwise.
    """
    if not time_str or len(time_str) != 4:
        return False
        
    try:
        hours, minutes = parse_time(time_str)
        return (
            hours is not None
            and minutes is not None
            and 0 <= hours <= 23
            and 0 <= minutes <= 59
        )
    except (ValueError, IndexError):
        return False

def format_date_range(start_date, end_date):
    """
    Format a date range for display.
    
    Args:
        start_date (datetime): The start date.
        end_date (datetime): The end date.
        
    Returns:
        str: Formatted date range string.
    """
    if start_date.year == end_date.year:
        if start_date.month == end_date.month:
            return f"{start_date.strftime('%-d')} - {end_date.strftime('%-d %b %Y')}"
        return f"{start_date.strftime('%-d %b')} - {end_date.strftime('%-d %b %Y')}"
    return f"{start_date.strftime('%-d %b %Y')} - {end_date.strftime('%-d %b %Y')}" 