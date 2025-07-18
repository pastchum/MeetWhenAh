from datetime import datetime, timedelta
from typing import List, Dict, Set, Tuple, Any
from collections import defaultdict
import math
import logging
import uuid

# Import from other

# Set up logging
logger = logging.getLogger(__name__)

# Constants
DEFAULT_SLEEP_HOURS = {
    "start": 2300,  # 11:00 PM
    "end": 700      # 7:00 AM
}
DEFAULT_MIN_BLOCK_SIZE = 2  # No of blocks (2 * 30 min blocks)
TIME_SLOT_SIZE = 30  # minutes
SENSITIVITY_THRESHOLD = 2  # Threshold for considering a block to be valid (e.g. if the number of participants changes by more than this threshold, the block is not valid)
MIN_PARTICIPANTS = 2  # Minimum number of participants in an event block

"""
Algorithm for calculating optimal meeting times:

Basic Flow:
1. Get the availability blocks of all participants and form a map of time slots to participants
2. Break up the availability into contiguous event blocks of time, where the event block size is the minimum availability block size
   For an event block to be valid: 
    a. The event block must be at least the minimum availability block size (e.g. 1 event block = 2 of each 30 min availability blocks)
    b. The event block must not include sleep hours
    c. The event block must not include any time slots where the number of participants changes drastically (e.g. from 2 to 10)
    d. The event block must not include any time slots where the number of participants is less than the minimum number of participants
3. Find the best event block by scoring the event block based on the (average) number of participants across the availability blocks in the event block and the duration of the event block
4. Return the best event block

Inputs:
    - Availability blocks of all participants for the given event
    - Minimum block size (Used to determine the minimum number of blocks for the given event)
    - Sleep hours (Optional) (Not implemented yet)
    - Minimum number of participants in an event block (Default: 2)
    - Sensitivity threshold (Default: 2)

Output:
    - Best event block 
    (Json: {
        "start_time": datetimetz, # Start time of the event block
        "end_time": datetimetz, # End time of the event block
        "participants": List[str], # List of the UUIDs of participants in the event block
        "participant_count": int, # Number of participants in the event block
        "duration": int # Duration of the event block in minutes (in minutes)
    })

Extensions:
1. Add sleep hours to the algorithm
2. Preferential time of day for event (e.g. morning, afternoon, evening)
"""

class Scheduler:
    """
    Class to process availability data and find optimal meeting times.
    This service handles the core scheduling logic for finding the best meeting times
    based on participants' availability and preferences.
    """
    def __init__(self, sleep_hours: dict = DEFAULT_SLEEP_HOURS, min_block_size: int = DEFAULT_MIN_BLOCK_SIZE, min_participants: int = MIN_PARTICIPANTS, sensitivity_threshold: int = SENSITIVITY_THRESHOLD):
        self.sleep_hours = sleep_hours
        self.min_block_size = min_block_size
        self.min_participants = min_participants
        self.sensitivity_threshold = sensitivity_threshold

    def _create_availability_map(self, availability_blocks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create a map of time slots to participants
        """
        """
        Availability blocks are in the format:
        {
            "start_time": str, # Date of the availability block
            "end_time": str, # Time of the availability block
            "event_id": str, # Event ID
            "user_uuid": str, # User UUID
        }
        The availability map is a map of time slots to participants.
        The time slot is a tuple of the date and the time, and the participants is the list of the user UUIDs.
        """
        availability_map = {}
        for block in availability_blocks:
            start_time = datetime.strptime(block["start_time"], "%Y-%m-%d %H:%M:%S")
            if start_time not in availability_map:
                availability_map[start_time] = [block["user_uuid"]]
            else:
                new_participants = availability_map[start_time] + [block["user_uuid"]]
                availability_map[start_time] = sorted(new_participants)
        return availability_map

    def _create_event_blocks(self, availability_map: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Create event blocks from the availability map
        """
        event_blocks = []
        max_block_size = self.min_block_size * 2
        sorted_slots = sorted(availability_map.keys())
        print("Sorted slots: ", sorted_slots)
        for time_slot in sorted_slots:
            # initialise the event block if minimum number of participants are available for any given availability block
            start_time = time_slot
            participants = availability_map[time_slot]
            intersection = set(participants)
            if len(participants) >= self.min_participants:
                # Scan through all subsequent blocks and merge consecutive ones as long as they have more than the minimum participants
                i = 1
                while i < max_block_size:
                    next_block = time_slot + timedelta(minutes=i * 30)
                    if next_block in availability_map:
                        new_intersection = intersection.intersection(set(availability_map[next_block]))
                        if len(new_intersection) >= self.min_participants:
                            intersection = new_intersection
                            i += 1
                        else:
                            break
                    else:
                        break
                if i >= self.min_block_size:
                    end_time = time_slot + timedelta(minutes=i * 30)
                    event_block_participants = sorted(list(intersection))
                    event_blocks.append({
                        "start_time": start_time.strftime("%Y-%m-%d %H:%M:%S"),
                        "end_time": end_time.strftime("%Y-%m-%d %H:%M:%S"),
                        "participants": event_block_participants,
                        "participant_count": len(event_block_participants),
                        "duration": i * 30
                    })

        return event_blocks

    def _is_valid_event_block(self, event_block: Dict[str, Any]) -> bool:
        """
        Check if the event block is valid
        """
        # check if the event block is within sleep hours
        if not self._is_within_sleep_hours(event_block):
            return False
        # check if the event block is within the sensitivity threshold
        if not self._is_within_sensitivity_threshold(event_block):
            return False
        # check if the event block is within the minimum number of participants
        if not self._is_within_minimum_participants(event_block):
            return False
        # check if the event block is within the minimum block size
        if not self._is_within_minimum_block_size(event_block):
            return False

        return True
    
    def _is_within_sleep_hours(self, event_block: Dict[str, Any]) -> bool:
        """
        Check if the event block is within sleep hours
        """
        #TODO when sleep hours are implemented
        return True
    
    def _is_within_sensitivity_threshold(self, event_block: Dict[str, Any]) -> bool:
        """
        Check if the event block is within the sensitivity threshold
        """
        #TODO: Implement this when sensitivity threshold is implemented
        return True
    
    def _is_within_minimum_block_size(self, event_block: Dict[str, Any]) -> bool:
        """
        Check if the event block is within the minimum block size
        """
        # Calculate the duration in minutes between start_time and end_time
        # Accepts both string and datetime for compatibility
        start = event_block["start_time"]
        end = event_block["end_time"]
        if isinstance(start, str):
            start = datetime.strptime(start, "%Y-%m-%d %H:%M:%S")
        if isinstance(end, str):
            end = datetime.strptime(end, "%Y-%m-%d %H:%M:%S")
        duration_minutes = (end - start).total_seconds() / 60
        min_duration = self.min_block_size * TIME_SLOT_SIZE
        if duration_minutes < min_duration:
            return False
        return True
    
    def _is_within_minimum_participants(self, event_block: Dict[str, Any]) -> bool:
        """
        Check if the event block is within the minimum number of participants
        """
        if len(event_block["participants"]) < self.min_participants:
            return False
        return True

    def _score_event_block(self, event_block: Dict[str, Any]) -> float:
        """
        Score the event block
        Metrics to score: 
        - Number of participants
        - Duration
        - Break ties by earliest start time
        """
        start = event_block["start_time"]
        end = event_block["end_time"]
        if isinstance(start, str):
            start = datetime.strptime(start, "%Y-%m-%d %H:%M:%S")
        if isinstance(end, str):
            end = datetime.strptime(end, "%Y-%m-%d %H:%M:%S")
        duration = (end - start).total_seconds() / 30
        participant_count = len(event_block["participants"])
        return participant_count * duration
    
    def _get_best_event_block(self, event_blocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Get the best event block
        """
        if not event_blocks:
            return []
        best_event_block = max(event_blocks, key=self._score_event_block)
        score = self._score_event_block(best_event_block)
        best_event_blocks = [event_block for event_block in event_blocks if self._score_event_block(event_block) == score]
        return best_event_blocks

    
    # Main function to process the availability blocks and return the best event block
    def _process_availability_blocks(self, availability_blocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process the availability blocks
        """
        availability_map = self._create_availability_map(availability_blocks)
        event_blocks = self._create_event_blocks(availability_map)
        valid_blocks = [event_block for event_block in event_blocks if self._is_valid_event_block(event_block)]
        return self._get_best_event_block(valid_blocks)

if __name__ == "__main__":
    scheduler = Scheduler()
    availability_blocks = [
            {"start_time": "2025-01-01 10:00:00", "end_time": "2025-01-01 10:30:00", "event_id": "1", "user_uuid": "1"},
            {"start_time": "2025-01-01 11:00:00", "end_time": "2025-01-01 11:30:00", "event_id": "1", "user_uuid": "2"},
            {"start_time": "2025-01-01 11:00:00", "end_time": "2025-01-01 11:30:00", "event_id": "1", "user_uuid": "1"},
            {"start_time": "2025-01-01 10:30:00", "end_time": "2025-01-01 11:00:00", "event_id": "1", "user_uuid": "1"},
                        {"start_time": "2025-01-01 10:30:00", "end_time": "2025-01-01 11:00:00", "event_id": "1", "user_uuid": "2"},
            {"start_time": "2025-01-01 10:30:00", "end_time": "2025-01-01 11:00:00", "event_id": "1", "user_uuid": "3"},
            {"start_time": "2025-01-01 11:30:00", "end_time": "2025-01-01 12:00:00", "event_id": "1", "user_uuid": "2"},
            {"start_time": "2025-01-01 12:00:00", "end_time": "2025-01-01 12:30:00", "event_id": "1", "user_uuid": "1"},
            {"start_time": "2025-01-01 12:30:00", "end_time": "2025-01-01 13:00:00", "event_id": "1", "user_uuid": "3"},
            {"start_time": "2025-01-01 13:00:00", "end_time": "2025-01-01 13:30:00", "event_id": "1", "user_uuid": "1"},
            {"start_time": "2025-01-01 12:30:00", "end_time": "2025-01-01 13:00:00", "event_id": "1", "user_uuid": "2"},
        ]
    print(scheduler._create_event_blocks(scheduler._create_availability_map(availability_blocks)))