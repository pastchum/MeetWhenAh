import { createClient } from '@supabase/supabase-js';

// Constants
const DEFAULT_SLEEP_HOURS = {
  start: 2300,  // 11:00 PM
  end: 700      // 7:00 AM
};
const DEFAULT_MIN_BLOCK_SIZE = 2;  // No of blocks (2 * 30 min blocks)
const TIME_SLOT_SIZE = 30;  // minutes
const SENSITIVITY_THRESHOLD = 2;  // Threshold for considering a block to be valid
const MIN_PARTICIPANTS = 2;  // Minimum number of participants in an event block
const MAX_MULTIPLIER = 2;  // Maximum multiplier for the minimum block size

interface AvailabilityBlock {
  start_time: string;
  end_time: string;
  event_id: string;
  user_uuid: string;
}

interface EventBlock {
  start_time: string;
  end_time: string;
  participants: string[];
  participant_count: number;
  duration: number;
}

interface SleepHours {
  start: number;
  end: number;
}

export class Scheduler {
  private sleepHours: SleepHours;
  private minBlockSize: number;
  private minParticipants: number;
  private sensitivityThreshold: number;
  private maxMultiplier: number;

  constructor(
    sleepHours: SleepHours = DEFAULT_SLEEP_HOURS,
    minBlockSize: number = DEFAULT_MIN_BLOCK_SIZE,
    minParticipants: number = MIN_PARTICIPANTS,
    sensitivityThreshold: number = SENSITIVITY_THRESHOLD,
    maxMultiplier: number = MAX_MULTIPLIER
  ) {
    this.sleepHours = sleepHours;
    this.minBlockSize = minBlockSize;
    this.minParticipants = minParticipants;
    this.sensitivityThreshold = sensitivityThreshold;
    this.maxMultiplier = maxMultiplier;
  }

  private createAvailabilityMap(availabilityBlocks: AvailabilityBlock[]): Map<string, string[]> {
    /**
     * Create a map of time slots to participants
     * 
     * Availability blocks are in the format:
     * {
     *   "start_time": string, // Date of the availability block
     *   "end_time": string, // Time of the availability block
     *   "event_id": string, // Event ID
     *   "user_uuid": string, // User UUID
     * }
     * 
     * The availability map is a map of time slots to participants.
     * The time slot is a string representation of the date and time, and the participants is the list of the user UUIDs.
     */
    const availabilityMap = new Map<string, string[]>();
    
    for (const block of availabilityBlocks) {
      const startTime = this.parseDateTime(block.start_time);
      const timeSlotKey = this.formatDateTime(startTime);
      
      if (!availabilityMap.has(timeSlotKey)) {
        availabilityMap.set(timeSlotKey, [block.user_uuid]);
      } else {
        const existingParticipants = availabilityMap.get(timeSlotKey)!;
        const newParticipants = [...existingParticipants, block.user_uuid];
        availabilityMap.set(timeSlotKey, newParticipants.sort());
      }
    }
    
    return availabilityMap;
  }

  private createEventBlocks(availabilityMap: Map<string, string[]>): EventBlock[] {
    /**
     * Create event blocks from the availability map
     */
    const eventBlocks: EventBlock[] = [];
    const maxBlockSize = this.minBlockSize * this.maxMultiplier;
    const sortedSlots = Array.from(availabilityMap.keys()).sort();
    
    console.log("Sorted slots: ", sortedSlots);
    
    for (const timeSlotKey of sortedSlots) {
      const startTime = this.parseDateTime(timeSlotKey);
      const participants = availabilityMap.get(timeSlotKey)!;
      let intersection = new Set(participants);
      
      if (participants.length >= this.minParticipants) {
        // Scan through all subsequent blocks and merge consecutive ones as long as they have more than the minimum participants
        let i = 1;
        while (i < maxBlockSize) {
          const nextBlockTime = new Date(startTime.getTime() + i * 30 * 60 * 1000);
          const nextBlockKey = this.formatDateTime(nextBlockTime);
          
          if (availabilityMap.has(nextBlockKey)) {
            const nextBlockParticipants = availabilityMap.get(nextBlockKey)!;
            const newIntersection = new Set([...intersection].filter(x => nextBlockParticipants.includes(x)));
            
            if (newIntersection.size >= this.minParticipants) {
              intersection = newIntersection;
              i += 1;
            } else {
              break;
            }
          } else {
            break;
          }
        }
        
        if (i >= this.minBlockSize) {
          const endTime = new Date(startTime.getTime() + i * 30 * 60 * 1000);
          const eventBlockParticipants = Array.from(intersection).sort();
          
          eventBlocks.push({
            start_time: this.formatDateTime(startTime),
            end_time: this.formatDateTime(endTime),
            participants: eventBlockParticipants,
            participant_count: eventBlockParticipants.length,
            duration: i * 30
          });
        }
      }
    }
    
    return eventBlocks;
  }

  private isValidEventBlock(eventBlock: EventBlock): boolean {
    /**
     * Check if the event block is valid
     */
    // check if the event block is within sleep hours
    if (!this.isWithinSleepHours(eventBlock)) {
      return false;
    }
    // check if the event block is within the sensitivity threshold
    if (!this.isWithinSensitivityThreshold(eventBlock)) {
      return false;
    }
    // check if the event block is within the minimum number of participants
    if (!this.isWithinMinimumParticipants(eventBlock)) {
      return false;
    }
    // check if the event block is within the minimum block size
    if (!this.isWithinMinimumBlockSize(eventBlock)) {
      return false;
    }

    return true;
  }

  private isWithinSleepHours(eventBlock: EventBlock): boolean {
    /**
     * Check if the event block is within sleep hours
     */
    // TODO: when sleep hours are implemented
    return true;
  }

  private isWithinSensitivityThreshold(eventBlock: EventBlock): boolean {
    /**
     * Check if the event block is within the sensitivity threshold
     */
    // TODO: Implement this when sensitivity threshold is implemented
    return true;
  }

  private isWithinMinimumBlockSize(eventBlock: EventBlock): boolean {
    /**
     * Check if the event block is within the minimum block size
     */
    const start = this.parseDateTime(eventBlock.start_time);
    const end = this.parseDateTime(eventBlock.end_time);
    const durationMinutes = (end.getTime() - start.getTime()) / (1000 * 60);
    const minDuration = this.minBlockSize * TIME_SLOT_SIZE;
    
    return durationMinutes >= minDuration;
  }

  private isWithinMinimumParticipants(eventBlock: EventBlock): boolean {
    /**
     * Check if the event block is within the minimum number of participants
     */
    return eventBlock.participants.length >= this.minParticipants;
  }

  private scoreEventBlock(eventBlock: EventBlock): number {
    /**
     * Score the event block
     * Metrics to score: 
     * - Number of participants
     * - Duration
     * - Break ties by earliest start time
     */
    const start = this.parseDateTime(eventBlock.start_time);
    const end = this.parseDateTime(eventBlock.end_time);
    const duration = (end.getTime() - start.getTime()) / (1000 * 60 * 30); // Convert to 30-minute blocks
    const participantCount = eventBlock.participants.length;
    
    return participantCount * duration;
  }

  private getBestEventBlock(eventBlocks: EventBlock[]): EventBlock[] {
    /**
     * Get the best event block
     */
    if (eventBlocks.length === 0) {
      return [];
    }
    
    const bestEventBlock = eventBlocks.reduce((best, current) => 
      this.scoreEventBlock(current) > this.scoreEventBlock(best) ? current : best
    );
    
    const bestScore = this.scoreEventBlock(bestEventBlock);
    const bestEventBlocks = eventBlocks.filter(eventBlock => 
      this.scoreEventBlock(eventBlock) === bestScore
    );
    
    return bestEventBlocks;
  }

  private processAvailabilityBlocks(availabilityBlocks: AvailabilityBlock[]): EventBlock[] {
    /**
     * Process the availability blocks
     */
    const availabilityMap = this.createAvailabilityMap(availabilityBlocks);
    const eventBlocks = this.createEventBlocks(availabilityMap);
    const validBlocks = eventBlocks.filter(eventBlock => this.isValidEventBlock(eventBlock));
    
    return this.getBestEventBlock(validBlocks);
  }

  private parseDateTime(datetimeStr: string): Date {
    /**
     * Parse datetime string in various formats including ISO format with timezone
     */
    // Try ISO format first (most common for database TIMESTAMPTZ)
    try {
      return new Date(datetimeStr.replace('Z', '+00:00'));
    } catch (error) {
      // Continue to next format
    }
    
    // Try the old format as fallback
    try {
      const [datePart, timePart] = datetimeStr.split(' ');
      const [year, month, day] = datePart.split('-').map(Number);
      const [hour, minute, second] = timePart.split(':').map(Number);
      return new Date(year, month - 1, day, hour, minute, second);
    } catch (error) {
      // Continue to next format
    }
    
    // Try ISO format without timezone
    try {
      return new Date(datetimeStr);
    } catch (error) {
      // Continue to next format
    }
    
    // If all else fails, raise an error
    throw new Error(`Unable to parse datetime string: ${datetimeStr}`);
  }

  private formatDateTime(dt: Date): string {
    /**
     * Format datetime to ISO format with timezone
     */
    return dt.toISOString();
  }

  public getBestMeetingTimes(availabilityBlocks: AvailabilityBlock[]): EventBlock[] {
    /**
     * Public method to get the best meeting times for an event
     */
    return this.processAvailabilityBlocks(availabilityBlocks);
  }
} 