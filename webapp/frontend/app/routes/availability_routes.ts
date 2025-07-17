import { ApiResponse } from "./events_routes";

export interface AvailabilityData {
    start_time: string;
    end_time: string;
    event_id: string;
    user_uuid?: string; // Optional since backend can derive it from username
  }
  
  export interface AvailabilityRequest {
    tele_id: string;
    event_id: string;
    availability_data: AvailabilityData[];
  }


/**
 * Get user availability for a specific event
 * Uses the existing /api/availability/{tele_id}/{event_id} endpoint
 * @param tele_id - The telegram id to get availability for
 * @param eventId - The event ID
 * @returns Promise<AvailabilityData[] | null> - The availability data or null if not found
 */
export async function getUserAvailability(tele_id: string, eventId: string): Promise<AvailabilityData[] | null> {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/availability/${tele_id}/${eventId}`, {
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
    tele_id: string, 
    eventId: string, 
    availabilityData: AvailabilityData[]
  ): Promise<boolean> {
    try {
      const requestBody: AvailabilityRequest = {
        tele_id,
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
 * Get user UUID by telegram id
 * Uses the existing /api/user/{tele_id} endpoint
 * @param tele_id - The telegram id to get UUID for
 * @returns Promise<string | null> - The user UUID or null if not found
 */
export async function getUserData(tele_id: string): Promise<{uuid: string, username: string} | null> {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/user/user-data-from-tele-id/${tele_id}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });
  
      if (!response.ok) {
        console.error(`Failed to fetch user UUID: ${response.status} ${response.statusText}`);
        return null;
      }
  
      const result: ApiResponse<{uuid: string, username: string}> = await response.json();
  
      if (result.status === 'success' && result.data) {
        return result.data;
      } else {
        console.error('Failed to get user data:', result.message);
        return null;
      }
    } catch (error) {
      console.error('Error fetching user data:', error);
      return null;
    }
  }


  /**
 * Get user UUID by username
 * Uses the existing /api/user/{username} endpoint
 * @param username - The username to get UUID for
 * @returns Promise<string | null> - The user UUID or null if not found
 */
  export async function getUserDataFromUsername(username: string): Promise<{uuid: string, username: string, tele_id: number} | null> {
    try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/user/user-data-from-username/${username}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });
  
      if (!response.ok) {
        console.error(`Failed to fetch user data: ${response.status} ${response.statusText}`);
        return null;
      }
  
      const result: ApiResponse<{uuid: string, username: string, tele_id: number}> = await response.json();
  
      if (result.status === 'success' && result.data) {
        return result.data;
      } else {
        console.error('Failed to get user data:', result.message);
        return null;
      }
    } catch (error) {
      console.error('Error fetching user data:', error);
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
  