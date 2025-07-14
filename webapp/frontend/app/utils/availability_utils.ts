import { ApiResponse } from "./events_utils";

export interface AvailabilityData {
    start_time: string;
    end_time: string;
    event_id: string;
    user_uuid?: string; // Optional since backend can derive it from username
  }
  
  export interface AvailabilityRequest {
    username: string;
    event_id: string;
    availability_data: AvailabilityData[];
  }


/**
 * Get user availability for a specific event
 * Uses the existing /api/availability/{username}/{event_id} endpoint
 * @param username - The username to get availability for
 * @param eventId - The event ID
 * @returns Promise<AvailabilityData[] | null> - The availability data or null if not found
 */
export async function getUserAvailability(username: string, eventId: string): Promise<AvailabilityData[] | null> {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/availability/${username}/${eventId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });
  
      if (!response.ok) {
        console.error(`Failed to fetch availability: ${response.status} ${response.statusText}`);
        return null;
      }
  
      const result: ApiResponse<AvailabilityData[]> = await response.json();
  
      if (result.status === 'success' && result.data) {
        return result.data;
      } else {
        console.error('Failed to get availability:', result.message);
        return null;
      }
    } catch (error) {
      console.error('Error fetching availability:', error);
      return null;
    }
  }
  
  /**
   * Update user availability for a specific event
   * Uses the existing POST /api/availability endpoint
   * @param username - The username to update availability for
   * @param eventId - The event ID
   * @param availabilityData - The availability data to update
   * @returns Promise<boolean> - True if successful, false otherwise
   */
  export async function updateUserAvailability(
    username: string, 
    eventId: string, 
    availabilityData: AvailabilityData[]
  ): Promise<boolean> {
    try {
      const requestBody: AvailabilityRequest = {
        username,
        event_id: eventId,
        availability_data: availabilityData,
      };
      console.log(requestBody);
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/save-availability`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });
  
      if (!response.ok) {
        console.error(`Failed to update availability: ${response.status} ${response.statusText}`);
        return false;
      }
  
      const result: ApiResponse<any> = await response.json();
  
      if (result.status === 'success') {
        return true;
      } else {
        console.error('Failed to update availability:', result.message);
        return false;
      }
    } catch (error) {
      console.error('Error updating availability:', error);
      return false;
    }
  }
  
  /**
 * Get user UUID by username
 * Uses the existing /api/user/{username}/uuid endpoint
 * @param username - The username to get UUID for
 * @returns Promise<string | null> - The user UUID or null if not found
 */
export async function getUserUuid(username: string): Promise<string | null> {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/user/${username}/uuid`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });
  
      if (!response.ok) {
        console.error(`Failed to fetch user UUID: ${response.status} ${response.statusText}`);
        return null;
      }
  
      const result: ApiResponse<{uuid: string}> = await response.json();
  
      if (result.status === 'success' && result.data) {
        return result.data.uuid;
      } else {
        console.error('Failed to get user UUID:', result.message);
        return null;
      }
    } catch (error) {
      console.error('Error fetching user UUID:', error);
      return null;
    }
  }

/**
 * Health check for the API
 * Uses the existing /webhook/health endpoint
 * @returns Promise<boolean> - True if API is healthy, false otherwise
 */
export async function checkApiHealth(): Promise<boolean> {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/webhook/health`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });
  
      if (!response.ok) {
        console.error(`Health check failed: ${response.status} ${response.statusText}`);
        return false;
      }
  
      const result = await response.json();
      return result.status === 'healthy';
    } catch (error) {
      console.error('Error checking API health:', error);
      return false;
    }
  }
  