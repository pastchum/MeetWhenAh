from datetime import datetime, timedelta
from .event_service import getEventSleepPreferences
from ..utils.date_utils import parse_time, format_time

def calculate_optimal_meeting_time(event_id, hours_available):
    """
    Calculate the optimal meeting time based on member availability and sleep preferences.
    
    Args:
        event_id (str): The event ID.
        hours_available (list): List of dictionaries containing availability data.
        
    Returns:
        tuple: A tuple of (best_date, best_time, max_attendees).
    """
    try:
        sleep_preferences = getEventSleepPreferences(event_id)
        if not sleep_preferences:
            return None, None, 0
            
        best_date = None
        best_time = None
        max_attendees = 0
        
        for day in hours_available:
            date = day['date']
            for time, users in day.items():
                if time == 'date':
                    continue
                    
                attendees = len(users)
                if attendees > max_attendees:
                    # Check if this time works with sleep preferences
                    if is_time_suitable(time, sleep_preferences):
                        max_attendees = attendees
                        best_date = date
                        best_time = time
                        
        return best_date, best_time, max_attendees
    except Exception as e:
        print(f"Error calculating optimal meeting time: {e}")
        return None, None, 0

def is_time_suitable(time, sleep_preferences):
    """
    Check if a time is suitable based on sleep preferences.
    
    Args:
        time (str): The time to check in HHMM format.
        sleep_preferences (list): List of tuples (username, sleep_start, sleep_end).
        
    Returns:
        bool: True if the time is suitable, False otherwise.
    """
    try:
        hours, minutes = parse_time(time)
        if hours is None or minutes is None:
            return False
            
        for _, sleep_start, sleep_end in sleep_preferences:
            if not sleep_start or not sleep_end:
                continue
                
            start_hours, start_minutes = parse_time(sleep_start)
            end_hours, end_minutes = parse_time(sleep_end)
            
            if start_hours is None or end_hours is None:
                continue
                
            # Convert to minutes for easier comparison
            time_mins = hours * 60 + minutes
            start_mins = start_hours * 60 + start_minutes
            end_mins = end_hours * 60 + end_minutes
            
            # Handle overnight sleep schedules
            if start_mins > end_mins:
                # Time is unsuitable if it falls between sleep start and midnight
                # or between midnight and sleep end
                if time_mins >= start_mins or time_mins <= end_mins:
                    return False
            else:
                # Time is unsuitable if it falls between sleep start and end
                if start_mins <= time_mins <= end_mins:
                    return False
                    
        return True
    except Exception as e:
        print(f"Error checking time suitability: {e}")
        return False

def format_availability_summary(availability_data):
    """
    Format availability data into a human-readable summary.
    
    Args:
        availability_data (list): List of dictionaries containing availability data.
        
    Returns:
        str: A formatted summary of availability.
    """
    try:
        if not availability_data:
            return "No availability data."
            
        summary = []
        for day in availability_data:
            date = day['date']
            times = day.get('times', [])
            
            if not times:
                continue
                
            # Sort times and group consecutive slots
            times.sort()
            time_ranges = []
            start = None
            prev = None
            
            for time in times:
                if not start:
                    start = time
                    prev = time
                    continue
                    
                # Check if times are consecutive (30-minute intervals)
                curr_hours, curr_minutes = parse_time(time)
                prev_hours, prev_minutes = parse_time(prev)
                
                if curr_hours is None or prev_hours is None:
                    continue
                    
                curr_mins = curr_hours * 60 + curr_minutes
                prev_mins = prev_hours * 60 + prev_minutes
                
                if curr_mins - prev_mins > 30:
                    # Add the completed range
                    time_ranges.append(f"{format_time(start)} - {format_time(prev)}")
                    start = time
                    
                prev = time
                
            # Add the last range
            if start:
                time_ranges.append(f"{format_time(start)} - {format_time(prev)}")
                
            if time_ranges:
                date_str = date.strftime("%d %b %Y")
                summary.append(f"{date_str}: {', '.join(time_ranges)}")
                
        return "\n".join(summary) if summary else "No continuous time slots found."
    except Exception as e:
        print(f"Error formatting availability summary: {e}")
        return "Error formatting availability data." 