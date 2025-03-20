from datetime import datetime, timedelta
from typing import List, Dict, Set, Tuple, Any
from collections import defaultdict
import math
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
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
    Class to process availability data and find optimal meeting times
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
    
    def find_optimal_meeting_times(self, hours_available: List[Dict]) -> Dict:
        """
        Find the optimal meeting times based on all participants' availability
        
        Args:
            hours_available: List of dictionaries containing date and availability data
                Each dict has a 'date' key and time keys (HHMM format) with lists of user IDs
        
        Returns:
            Dict with optimal meeting information
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
        """Calculate duration between two time strings in minutes"""
        start_minutes = self._time_to_minutes(start_time)
        end_minutes = self._time_to_minutes(end_time)
        
        # Add 30 minutes because end_time is the start of the last slot
        duration = end_minutes - start_minutes + TIME_SLOT_SIZE
        
        # Handle case where end_time is earlier than start_time (crossing midnight)
        if duration <= 0:
            duration += 24 * 60
            
        return duration
    
    def _get_end_time(self, time_str: str) -> str:
        """Get end time string by adding TIME_SLOT_SIZE to the given time"""
        minutes = self._time_to_minutes(time_str) + TIME_SLOT_SIZE
        if minutes >= 24 * 60:
            minutes -= 24 * 60
        return self._minutes_to_time(minutes)
    
    def _score_block(self, block: Dict, total_participants: int) -> float:
        """
        Calculate a score for a block based on participants, duration, and time of day
        
        Args:
            block: Dict with block information
            total_participants: Total number of participants across all days
            
        Returns:
            Score as a float
        """
        participant_ratio = block['participant_count'] / total_participants if total_participants > 0 else 0
        
        # Base score is the participant ratio (0-1)
        score = participant_ratio
        
        # Bonus for longer blocks (up to 2 hours)
        duration_hours = min(2, block['duration'] / 60)
        duration_bonus = duration_hours / 2  # 0-1 scale
        
        # Time of day factor - prefer mid-day (9AM-5PM)
        start_minutes = self._time_to_minutes(block['start_time'])
        
        # Time of day is a bell curve centered at 12:00 (720 minutes)
        mid_day = 720  # 12:00 PM in minutes
        time_diff = abs(start_minutes - mid_day)
        
        # Convert to a 0-1 scale (1 is best - at 12:00)
        # 8 hours (480 minutes) range for working hours 
        time_factor = max(0, 1 - (time_diff / 480))
        
        # Penalize for sleep time blocks
        sleep_penalty = 0.5 if self._is_sleep_time(block['start_time']) or self._is_sleep_time(block['end_time']) else 1.0
        
        # Calculate final score - participant ratio is most important
        final_score = (score * 0.6) + (duration_bonus * 0.2) + (time_factor * 0.2)
        final_score *= sleep_penalty
        
        return final_score
    
    def _find_best_slots(self, hours_available: List[Dict]) -> List[Dict]:
        """
        Find the best timeslots across all days
        
        Args:
            hours_available: List of dict with date and availability data
            
        Returns:
            List of best blocks with scores
        """
        all_blocks = []
        total_participants = self._get_total_participant_count(hours_available)
        
        for day in hours_available:
            date = day['date']
            day_copy = day.copy()  # Make a copy to avoid modifying the original
            
            # Find contiguous blocks for this day
            blocks = self._find_contiguous_blocks(day_copy)
            
            for block in blocks:
                block['date'] = date
                block['score'] = self._score_block(block, total_participants)
                all_blocks.append(block)
        
        return all_blocks
    
    def _get_total_participant_count(self, hours_available: List[Dict]) -> int:
        """Get the count of unique participants across all days"""
        all_participants = set()
        
        for day in hours_available:
            for key, participants in day.items():
                if key != 'date' and isinstance(participants, list):
                    all_participants.update(participants)
        
        return len(all_participants)

def calculate_optimal_meeting_time(hours_available, user_sleep_hours=None, min_block_size=DEFAULT_MIN_BLOCK_SIZE):
    """
    Calculate the optimal meeting time based on participant availability
    
    Args:
        hours_available: List of dicts with date and availability data
        user_sleep_hours: Optional dict with sleep hours for participants
        min_block_size: Minimum contiguous block size in minutes
        
    Returns:
        Dict with optimal meeting information
    """
    processor = AvailabilityProcessor(sleep_hours=user_sleep_hours, min_block_size=min_block_size)
    return processor.find_optimal_meeting_times(hours_available) 