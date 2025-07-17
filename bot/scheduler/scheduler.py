from datetime import datetime, timedelta
from typing import List, Dict, Set, Tuple, Any
from collections import defaultdict
import math
import logging
import uuid

# Import from services
from services.database_service import getEntry, setEntry, updateEntry

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
        availability_map = defaultdict(set)
        for block in availability_blocks:
            start_time = datetime.strptime(block["start_time"], "%Y-%m-%d %H:%M:%S")
            end_time = datetime.strptime(block["end_time"], "%Y-%m-%d %H:%M:%S")
            for time_slot in range(start_time, end_time, timedelta(minutes=TIME_SLOT_SIZE)):
                availability_map[time_slot].add(block["user_uuid"])
        return availability_map

    def _create_event_blocks(self, availability_map: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Create event blocks from the availability map
        """
        event_blocks = []
        for time_slot, participants in availability_map.items():
            # initialise the event block if minimum number of participants are available for any given availability block
            # Scan through all subsequent blocks and merge consecutive ones as long as they have more than the minimum participants
            sorted_slots = sorted(availability_map.keys())
            i = 0
            while i < len(sorted_slots):
                slot = sorted_slots[i]
                participants = availability_map[slot]
                if len(participants) >= self.min_participants:
                    start_time = slot
                    end_time = slot + timedelta(minutes=TIME_SLOT_SIZE)
                    merged_participants = set(participants)
                    j = i + 1
                    while j < len(sorted_slots):
                        next_slot = sorted_slots[j]
                        # Check if next_slot is consecutive
                        if (next_slot - end_time) == timedelta(0):
                            next_participants = availability_map[next_slot]
                            if len(next_participants) >= self.min_participants:
                                end_time = next_slot + timedelta(minutes=TIME_SLOT_SIZE)
                                merged_participants = merged_participants & set(next_participants)
                                j += 1
                                continue
                        break
                    block = {
                        "start_time": start_time,
                        "end_time": end_time,
                        "participants": list(merged_participants)
                    }
                    if self._is_valid_event_block(block):
                        event_blocks.append(block)
                    i = j
                else:
                    i += 1

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
        #TODO: Implement this
        return True
    
    def _is_within_sensitivity_threshold(self, event_block: Dict[str, Any]) -> bool:
        """
        Check if the event block is within the sensitivity threshold
        """
        #TODO: Implement this
        return True
    
    def _is_within_minimum_block_size(self, event_block: Dict[str, Any]) -> bool:
        """
        Check if the event block is within the minimum block size
        """
        #TODO: Implement this
        return True
    
    def _is_within_minimum_participants(self, event_block: Dict[str, Any]) -> bool:
        """
        Check if the event block is within the minimum number of participants
        """
        #TODO: Implement this
        return True

    def _score_event_block(self, event_block: Dict[str, Any]) -> float:
        """
        Score the event block
        """
        #TODO: Implement this
        return 0
    
    def _get_best_event_block(self, event_blocks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get the best event block
        """
        return max(event_blocks, key=self._score_event_block)
    
    # Main function to process the availability blocks and return the best event block
    def _process_availability_blocks(self, availability_blocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process the availability blocks
        """
        availability_map = self._create_availability_map(availability_blocks)
        event_blocks = self._create_event_blocks(availability_map)
        return self._get_best_event_block(event_blocks)
