from datetime import datetime, timedelta
from typing import List, Dict, Set, Tuple, Any
from collections import defaultdict
import math
import logging
import uuid
from .database_service import getEntry, setEntry, updateEntry
from .event_service import getEvent

# Set up logging
logger = logging.getLogger(__name__)

# Constants
DEFAULT_SLEEP_HOURS = {
    "start": 2300,  # 11:00 PM
    "end": 700      # 7:00 AM
}
DEFAULT_MIN_BLOCK_SIZE = 60  # minutes
TIME_SLOT_SIZE = 30  # minutes

class AvailabilityProcessor:
    """
    Class to process availability data and find optimal meeting times.
    This service handles the core scheduling logic for finding the best meeting times
    based on participants' availability and preferences.
    """
    def __init__(self, sleep_hours=None, min_block_size=DEFAULT_MIN_BLOCK_SIZE):
        """
        Initialize the processor with configuration
        
        Args:
            sleep_hours: Dict with 'start' and 'end' keys specifying sleep time in military format (e.g. 2300 for 11pm)
            min_block_size: Minimum size of contiguous blocks in minutes
        """
        self.sleep_hours = sleep_hours or DEFAULT_SLEEP_HOURS
        self.min_block_size = min_block_size

    def find_optimal_meeting_times(self, hours_available: List[Dict]) -> Dict:
        """
        Find the optimal meeting times based on all participants' availability
        
        Args:
            hours_available: List of dictionaries containing date and availability data
                Each dict has a 'date' key and time keys (HHMM format) with lists of user IDs
        
        Returns:
            Dict with optimal meeting information including:
            - final_date: The selected date
            - final_start_timing: Start time in HHMM format
            - final_end_timing: End time in HHMM format
            - max_participants: Number of participants available
            - participants: List of participant IDs
            - score: Quality score of the time slot
        """
        best_slots = self._find_best_slots(hours_available)
        
        if not best_slots:
            return {
                'final_date': None,
                'final_start_timing': None,
                'final_end_timing': None,
                'max_participants': 0,
                'participants': []
            }
        
        # Sort by score (descending)
        best_slots.sort(key=lambda x: x['score'], reverse=True)
        best_slot = best_slots[0]
        
        return {
            'final_date': best_slot['date'],
            'final_start_timing': best_slot['start_time'],
            'final_end_timing': best_slot['end_time'],
            'max_participants': best_slot['participant_count'],
            'participants': best_slot['participants'],
            'score': best_slot['score']
        }

    # Private helper methods
    def _time_to_minutes(self, time_str: str) -> int:
        """Convert time string in format 'HHMM' to minutes from midnight"""
        hours = int(time_str[:2])
        minutes = int(time_str[2:])
        return hours * 60 + minutes
    
    def _minutes_to_time(self, minutes: int) -> str:
        """Convert minutes from midnight to time string in format 'HHMM'"""
        hours = minutes // 60
        mins = minutes % 60
        return f"{hours:02d}{mins:02d}"
    
    def _is_sleep_time(self, time_str: str) -> bool:
        """Check if a given time is during the sleep hours"""
        minutes = self._time_to_minutes(time_str)
        sleep_start = self._time_to_minutes(str(self.sleep_hours["start"]))
        sleep_end = self._time_to_minutes(str(self.sleep_hours["end"]))
        
        # Handle case where sleep crosses midnight
        if sleep_start > sleep_end:
            return minutes >= sleep_start or minutes < sleep_end
        else:
            return minutes >= sleep_start and minutes < sleep_end

    def _find_contiguous_blocks(self, day_data: Dict, min_block_size: int = None) -> List[Dict]:
        """
        Find contiguous blocks of availability in a day
        
        Args:
            day_data: Dict with time slots and participant lists
            min_block_size: Minimum block size in minutes (defaults to self.min_block_size)
        
        Returns:
            List of dicts with start_time, end_time, and participants
        """
        if min_block_size is None:
            min_block_size = self.min_block_size
            
        min_slots = min_block_size // TIME_SLOT_SIZE
        blocks = []
        
        # Get all time slots as a sorted list, excluding the date key
        time_slots = sorted([t for t in day_data.keys() if t != 'date'])
        
        # Track current block participants and start time
        current_participants = set()
        block_start = None
        last_time = None
        
        for time_slot in time_slots:
            participants = set(day_data[time_slot])
            
            # Skip sleep times if not all participants are available
            if self._is_sleep_time(time_slot) and len(participants) < len(set().union(*[set(day_data[t]) for t in time_slots if t != 'date'])):
                # If we were building a block, check if it meets minimum size
                if block_start is not None:
                    block_duration = self._calculate_duration(block_start, last_time)
                    if block_duration >= min_block_size:
                        blocks.append({
                            'start_time': block_start,
                            'end_time': self._get_end_time(last_time),
                            'participants': list(current_participants),
                            'participant_count': len(current_participants),
                            'duration': block_duration
                        })
                
                # Reset block tracking
                block_start = None
                current_participants = set()
                last_time = None
                continue
            
            # If this is the start of a new block
            if block_start is None and participants:
                block_start = time_slot
                current_participants = participants
            
            # If continuing a block with the same participants
            elif block_start is not None and participants == current_participants:
                pass  # Just continue the current block
            
            # If continuing a block with different participants
            elif block_start is not None and participants:
                # Calculate the overlap and update current participants
                overlap = current_participants.intersection(participants)
                
                # If there's no overlap or less than 2 participants, end the current block
                if not overlap or len(overlap) < 2:
                    block_duration = self._calculate_duration(block_start, last_time)
                    if block_duration >= min_block_size:
                        blocks.append({
                            'start_time': block_start,
                            'end_time': self._get_end_time(last_time),
                            'participants': list(current_participants),
                            'participant_count': len(current_participants),
                            'duration': block_duration
                        })
                    
                    # Start a new block
                    block_start = time_slot
                    current_participants = participants
                else:
                    # Continue with the overlap
                    current_participants = overlap
            
            # If we reach a slot with no participants
            elif block_start is not None and not participants:
                block_duration = self._calculate_duration(block_start, last_time)
                if block_duration >= min_block_size:
                    blocks.append({
                        'start_time': block_start,
                        'end_time': self._get_end_time(last_time),
                        'participants': list(current_participants),
                        'participant_count': len(current_participants),
                        'duration': block_duration
                    })
                
                # Reset block tracking
                block_start = None
                current_participants = set()
                last_time = None
                continue
            
            last_time = time_slot
        
        # Add the last block if we were building one
        if block_start is not None:
            block_duration = self._calculate_duration(block_start, last_time)
            if block_duration >= min_block_size:
                blocks.append({
                    'start_time': block_start,
                    'end_time': self._get_end_time(last_time),
                    'participants': list(current_participants),
                    'participant_count': len(current_participants),
                    'duration': block_duration
                })
        
        return blocks

    def _calculate_duration(self, start_time: str, end_time: str) -> int:
        """Calculate duration between two times in minutes"""
        start_mins = self._time_to_minutes(start_time)
        end_mins = self._time_to_minutes(end_time)
        
        if end_mins < start_mins:
            end_mins += 24 * 60  # Add 24 hours if end time is next day
            
        return end_mins - start_mins + TIME_SLOT_SIZE

    def _get_end_time(self, time_str: str) -> str:
        """Get the end time of a time slot"""
        minutes = self._time_to_minutes(time_str)
        return self._minutes_to_time(minutes + TIME_SLOT_SIZE)

    def _score_block(self, block: Dict, total_participants: int) -> float:
        """
        Score a time block based on various factors:
        - Number of participants
        - Duration of the block
        - Time of day (prefer normal hours)
        """
        # Base score is the ratio of participants
        score = block['participant_count'] / total_participants
        
        # Bonus for longer blocks
        duration_bonus = min(block['duration'] / (4 * 60), 1.0)  # Cap at 4 hours
        score += duration_bonus * 0.2
        
        # Penalty for sleep hours
        if self._is_sleep_time(block['start_time']) or self._is_sleep_time(block['end_time']):
            score *= 0.5
        
        return score

    def _find_best_slots(self, hours_available: List[Dict]) -> List[Dict]:
        """Find the best time slots across all days"""
        best_slots = []
        total_participants = self._get_total_participant_count(hours_available)
        
        for day_data in hours_available:
            blocks = self._find_contiguous_blocks(day_data)
            
            for block in blocks:
                block['date'] = day_data['date']
                block['score'] = self._score_block(block, total_participants)
                best_slots.append(block)
        
        return best_slots

    def _get_total_participant_count(self, hours_available: List[Dict]) -> int:
        """Get the total number of unique participants"""
        all_participants = set()
        for day_data in hours_available:
            for time_slot in day_data:
                if time_slot != 'date':
                    all_participants.update(day_data[time_slot])
        return len(all_participants)

def calculate_optimal_meeting_time(hours_available, user_sleep_hours=None, min_block_size=DEFAULT_MIN_BLOCK_SIZE):
    """
    Convenience function to calculate optimal meeting time
    
    Args:
        hours_available: List of dictionaries containing availability data
        user_sleep_hours: Optional dict with sleep preferences
        min_block_size: Minimum block size in minutes
    
    Returns:
        Dict with optimal meeting information
    """
    processor = AvailabilityProcessor(sleep_hours=user_sleep_hours, min_block_size=min_block_size)
    return processor.find_optimal_meeting_times(hours_available)

def format_availability_summary(event_id: str, username: str) -> str:
    """Format a summary of a user's availability for an event"""
    event = getEvent(event_id)
    if not event:
        return "Event not found"
    
    availability = getEntry("availability", "event_id", event_id)
    if not availability or username not in availability:
        return "No availability data found"
    
    user_availability = availability[username]
    if not user_availability:
        return "No availability data found"
    
    # Format the summary
    summary = f"Your availability for {event['name']}:\n\n"
    
    # Group availability by date
    by_date = defaultdict(list)
    for slot in user_availability:
        date = slot['date']
        time = f"{slot['start_time']}-{slot['end_time']}"
        by_date[date].append(time)
    
    # Format each date's availability
    for date in sorted(by_date.keys()):
        summary += f"{date}:\n"
        for time in sorted(by_date[date]):
            summary += f"  {time}\n"
        summary += "\n"
    
    return summary 