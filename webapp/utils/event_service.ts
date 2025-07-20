import { supabase } from '@/lib/db';
import { Scheduler } from './scheduler';

export interface EventData {
  event_id: string;
  event_name: string;
  event_description: string;
  event_type: string;
  start_date: string;
  end_date: string;
  start_hour: string;
  end_hour: string;
  creator: string;
  created_at: string;
  updated_at: string;
  participants?: string[];
}

export interface EventBlock {
  start_time: string;
  end_time: string;
  participants: string[];
  duration: number;
  participant_count: number;
}

export class EventService {
  /**
   * Get event details by ID
   */
  async getEvent(eventId: string): Promise<EventData | null> {
    try {
      const { data, error } = await supabase
        .from('events')
        .select('*')
        .eq('event_id', eventId)
        .single();

      if (error) {
        console.error('Error getting event:', error);
        return null;
      }

      return data;
    } catch (error) {
      console.error('Error getting event:', error);
      return null;
    }
  }

  /**
   * Create a new event and return its ID
   */
  async createEvent(
    name: string,
    description: string,
    startDate: string,
    endDate: string,
    creatorTeleId: string,
    autoJoin: boolean = true,
    eventType: string = "general",
    startHour: string = "00:00:00.000000+08:00",
    endHour: string = "23:30:00.000000+08:00"
  ): Promise<string | null> {
    try {
      // Get creator details
      const { data: creatorData, error: creatorError } = await supabase
        .from('users')
        .select('uuid')
        .eq('tele_id', creatorTeleId)
        .single();

      if (creatorError || !creatorData) {
        console.error('Creator not found:', creatorTeleId);
        return null;
      }

      const eventId = crypto.randomUUID();
      const now = new Date().toISOString();
      
      const eventData = {
        event_id: eventId,
        event_name: name,
        event_description: description,
        event_type: eventType,
        start_date: new Date(startDate).toISOString(),
        end_date: new Date(endDate).toISOString(),
        start_hour: startHour,
        end_hour: endHour,
        creator: creatorData.uuid,
        created_at: now,
        updated_at: now
      };

      const { error } = await supabase
        .from('events')
        .insert(eventData);

      if (error) {
        console.error('Error creating event:', error);
        return null;
      }

      return eventId;
    } catch (error) {
      console.error('Error creating event:', error);
      return null;
    }
  }

  /**
   * Add a user to an event's participants
   */
  async joinEvent(eventId: string, userTeleId: string): Promise<boolean> {
    try {
      // Get user details
      const { data: userData, error: userError } = await supabase
        .from('users')
        .select('uuid')
        .eq('tele_id', userTeleId)
        .single();

      if (userError || !userData) {
        console.error('User not found:', userTeleId);
        return false;
      }

      // Get current event
      const event = await this.getEvent(eventId);
      if (!event) {
        console.error('Event not found:', eventId);
        return false;
      }

      // Check if user is already a participant
      const participants = event.participants || [];
      if (participants.includes(userData.uuid)) {
        return true; // Already a participant
      }

      // Add user to participants
      const { error } = await supabase
        .from('events')
        .update({
          participants: [...participants, userData.uuid],
          updated_at: new Date().toISOString()
        })
        .eq('event_id', eventId);

      if (error) {
        console.error('Error joining event:', error);
        return false;
      }

      return true;
    } catch (error) {
      console.error('Error joining event:', error);
      return false;
    }
  }

  /**
   * Get sleep preferences for all participants in an event
   */
  async getEventSleepPreferences(eventId: string): Promise<Record<string, { start: string; end: string }>> {
    try {
      const event = await this.getEvent(eventId);
      if (!event) {
        return {};
      }

      const participants = event.participants || [];
      const sleepPrefs: Record<string, { start: string; end: string }> = {};

      for (const userUuid of participants) {
        const { data: userData } = await supabase
          .from('users')
          .select('sleep_start, sleep_end')
          .eq('uuid', userUuid)
          .single();

        if (userData && userData.sleep_start && userData.sleep_end) {
          sleepPrefs[userUuid] = {
            start: userData.sleep_start,
            end: userData.sleep_end
          };
        }
      }

      return sleepPrefs;
    } catch (error) {
      console.error('Error getting sleep preferences:', error);
      return {};
    }
  }

  /**
   * Get all events that a user is a member of
   */
  async getUserEvents(userTeleId: string): Promise<Array<{ id: string; name: string }>> {
    try {
      // Get user details
      const { data: userData, error: userError } = await supabase
        .from('users')
        .select('uuid')
        .eq('tele_id', userTeleId)
        .single();

      if (userError || !userData) {
        return [];
      }

      // Get events where user is a participant
      const { data: events, error } = await supabase
        .from('events')
        .select('event_id, event_name')
        .contains('participants', [userData.uuid]);

      if (error) {
        console.error('Error getting user events:', error);
        return [];
      }

      return events.map(event => ({
        id: event.event_id,
        name: event.event_name || 'Unnamed Event'
      }));
    } catch (error) {
      console.error('Error getting user events:', error);
      return [];
    }
  }

  /**
   * Get the best time for an event using the scheduler
   */
  async getEventBestTime(eventId: string): Promise<EventBlock[]> {
    try {
      // Get all availability blocks for the event
      const { data: availabilityBlocks, error } = await supabase
        .from('availability_blocks')
        .select('*')
        .eq('event_id', eventId);

      if (error || !availabilityBlocks) {
        console.error('Error getting availability blocks:', error);
        return [];
      }

      // Use the scheduler to find the best meeting times
      const scheduler = new Scheduler();
      const bestTimes = scheduler.getBestMeetingTimes(availabilityBlocks);
      
      return bestTimes;
    } catch (error) {
      console.error('Error getting event best time:', error);
      return [];
    }
  }
} 