import { supabase } from '@/lib/db';

export interface AvailabilityData {
  user_uuid: string;
  event_id: string;
  start_time: string;
  end_time: string;
}

export interface FrontendAvailabilityData {
  date: string;
  time: string;
}

export class AvailabilityService {
  /**
   * Get a user's availability for an event
   */
  async getUserAvailability(teleId: string, eventId: string): Promise<AvailabilityData[]> {
    try {
      // Get user details
      const { data: userData, error: userError } = await supabase
        .from('users')
        .select('uuid')
        .eq('tele_id', teleId)
        .single();

      if (userError || !userData) {
        console.error('User not found:', teleId);
        return [];
      }

      // Get availability blocks for the event
      const { data: availabilityBlocks, error } = await supabase
        .from('availability_blocks')
        .select('*')
        .eq('event_id', eventId);

      if (error || !availabilityBlocks) {
        console.error('Error getting availability blocks:', error);
        return [];
      }

      // Filter for this user's availability
      const userAvailability = availabilityBlocks.filter(
        block => block.user_uuid === userData.uuid
      );

      return userAvailability;
    } catch (error) {
      console.error('Error getting user availability:', error);
      return [];
    }
  }

  /**
   * Update a user's availability for an event
   */
  async updateUserAvailability(
    teleId: string,
    eventId: string,
    availabilityData: FrontendAvailabilityData[]
  ): Promise<boolean> {
    try {
      // Get user details
      const { data: userData, error: userError } = await supabase
        .from('users')
        .select('uuid')
        .eq('tele_id', teleId)
        .single();

      if (userError || !userData) {
        console.error('User not found:', teleId);
        return false;
      }

      // Delete all existing availability blocks for this user and event
      const { error: deleteError } = await supabase
        .from('availability_blocks')
        .delete()
        .eq('user_uuid', userData.uuid)
        .eq('event_id', eventId);

      if (deleteError) {
        console.error('Error deleting availability:', deleteError);
        return false;
      }

      // If no new availability data, we're done
      if (!availabilityData || availabilityData.length === 0) {
        return true;
      }

      // Transform availability data to include user_uuid and convert to scheduler format
      const newAvailabilityData: AvailabilityData[] = [];
      
      for (const item of availabilityData) {
        const { date, time } = item;
        
        if (date && time) {
          // Convert time from "1430" format to "14:30:00" format
          const hours = Math.floor(parseInt(time) / 100);
          const minutes = parseInt(time) % 100;
          const timeFormatted = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:00`;
          
          // Create start_time and end_time for 30-minute blocks
          const startTime = `${date} ${timeFormatted}`;
          
          // Calculate end_time (30 minutes later)
          const startDate = new Date(startTime);
          const endDate = new Date(startDate.getTime() + 30 * 60 * 1000); // Add 30 minutes
          const endTime = endDate.toISOString().slice(0, 19).replace('T', ' '); // Format as "YYYY-MM-DD HH:MM:SS"
          
          const blockData: AvailabilityData = {
            start_time: startTime,
            end_time: endTime,
            event_id: eventId,
            user_uuid: userData.uuid
          };
          
          newAvailabilityData.push(blockData);
        }
      }

      // Insert new availability data
      if (newAvailabilityData.length > 0) {
        const { error: insertError } = await supabase
          .from('availability_blocks')
          .insert(newAvailabilityData);

        if (insertError) {
          console.error('Error inserting availability:', insertError);
          return false;
        }
      }

      return true;
    } catch (error) {
      console.error('Error updating availability:', error);
      return false;
    }
  }

  /**
   * Get all availability data for an event, grouped by user
   */
  async getEventAvailability(eventId: string): Promise<Record<string, AvailabilityData[]>> {
    try {
      // Get all availability blocks for the event
      const { data: availabilityBlocks, error } = await supabase
        .from('availability_blocks')
        .select('*')
        .eq('event_id', eventId);

      if (error || !availabilityBlocks) {
        console.error('Error getting event availability:', error);
        return {};
      }

      // Group by user
      const availabilityByUser: Record<string, AvailabilityData[]> = {};
      
      for (const block of availabilityBlocks) {
        const userUuid = block.user_uuid;
        if (userUuid) {
          // Get user details to get tele_id
          const { data: userData } = await supabase
            .from('users')
            .select('tele_id')
            .eq('uuid', userUuid)
            .single();

          if (userData) {
            const teleId = userData.tele_id;
            if (!availabilityByUser[teleId]) {
              availabilityByUser[teleId] = [];
            }
            availabilityByUser[teleId].push(block);
          }
        }
      }

      return availabilityByUser;
    } catch (error) {
      console.error('Error getting event availability:', error);
      return {};
    }
  }

  /**
   * Format a summary of a user's availability for an event
   */
  async formatAvailabilitySummary(eventId: string, teleId: string): Promise<string> {
    try {
      // Get event details
      const { data: eventData, error: eventError } = await supabase
        .from('events')
        .select('event_name')
        .eq('event_id', eventId)
        .single();

      if (eventError || !eventData) {
        return "Event not found";
      }

      // Get user availability
      const userAvailability = await this.getUserAvailability(teleId, eventId);
      if (!userAvailability || userAvailability.length === 0) {
        return "No availability data found";
      }

      // Format the summary
      const eventName = eventData.event_name || "Unknown Event";
      let summary = `Your availability for ${eventName}:\n\n`;

      // Group availability by date
      const byDate: Record<string, string[]> = {};
      
      for (const availability of userAvailability) {
        const startTime = availability.start_time;
        if (startTime) {
          // Extract date from start_time
          const date = startTime.split(' ')[0];
          const time = startTime.split(' ')[1];
          
          if (!byDate[date]) {
            byDate[date] = [];
          }
          byDate[date].push(time);
        }
      }

      // Format each date's availability
      const sortedDates = Object.keys(byDate).sort();
      for (const date of sortedDates) {
        summary += `${date}:\n`;
        const sortedTimes = byDate[date].sort();
        for (const time of sortedTimes) {
          summary += `  ${time}\n`;
        }
        summary += "\n";
      }

      return summary;
    } catch (error) {
      console.error('Error formatting availability summary:', error);
      return "Error formatting availability summary";
    }
  }
} 