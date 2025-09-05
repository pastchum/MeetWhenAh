import { supabase } from '@/lib/db';

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
  min_participants: number;
  min_duration_blocks: number;
  max_duration_blocks: number;
  timezone?: string;
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
    token: string,
    event_id: string,
    event_name: string,
    event_details: string,
    start: string,
    end: string,
    creator: string,
    event_type: string = "general",
    start_hour: string = "00:00:00.000000+08:00",
    end_hour: string = "23:30:00.000000+08:00"
  ): Promise<string | null> {
    try {
      const body = { token, event_id, event_name, event_details, start, end, creator, event_type, start_hour, end_hour }
      console.log('service: ', body);
      const response = await fetch(process.env.API_URL + '/api/event/create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(body),
      });
      const result = await response.json();
      console.log('service: ', result);
      return result.data.event_id;
    } catch (error) {
      console.error('Error creating event:', error);
      return null;
    }
  }

  /**
   * confirm an event
   */
  async confirmEvent(eventId: string, bestStartTime: string, bestEndTime: string): Promise<boolean> {
    try {
      const { error } = await supabase
        .from('event_confirmations')
        .insert({
          event_id: eventId,
          best_start_time: bestStartTime,
          best_end_time: bestEndTime
        });

      if (error) {
        console.error('Error confirming event:', error);
        return false;
      }

      return true;
    } catch (error) {
      console.error('Error confirming event:', error);
      return false;
    }
  }
  
  /**
   * Add a user to an event's participants
   */
  /*
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
    */

  /**
   * Get sleep preferences for all participants in an event
   */
  /*
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
    */

  /**
   * Get all events that a user is a member of
   */
  async getUserEvents(userTeleId: string): Promise<EventData[]> {
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

      // set to 00:00 of the current date
      const currentDate = new Date().toISOString().split('T')[0] + 'T00:00:00.000000+08:00';
      console.log(currentDate);

      // Get events where user is a participant
      const { data: events, error } = await supabase
        .from('events')
        .select('*')
        .eq('creator', userData.uuid)
        .gte('end_date', currentDate)
        .order('created_at', { ascending: false });

      if (error) {
        console.error('Error getting user events:', error);
        return [];
      }

      return events;
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
      const data = {
        event_id: eventId,
      }
      const response = await fetch(process.env.API_URL + '/api/event/get-best-time', {
        method: 'POST',
        body: JSON.stringify(data),
      });
      const result = await response.json();
      console.log(result);
      return result.data;
    } catch (error) {
      console.error('Error getting event best time:', error);
      return [];
    }
  }
} 