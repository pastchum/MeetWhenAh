/**
 * Events utility functions for interacting with the backend API
 * Based on available endpoints in server.py
 */

export interface EventDetails {
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
}

export interface ApiResponse<T> {
  status: 'success' | 'error';
  data?: T;
  message?: string;
}

/**
 * Get event details by event ID
 * Uses the existing /api/event/{event_id} endpoint
 * @param eventId - The event ID to retrieve
 * @returns Promise<EventDetails | null> - The event details or null if not found
 */
export async function getEvent(eventId: string): Promise<EventDetails | null> {
  if (!eventId) {
    console.error('Event ID is required');
    return null;
  }
  try {
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/event/${eventId}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      console.error(`Failed to fetch event: ${response.status} ${response.statusText}`);
      return null;
    }

    const result: ApiResponse<EventDetails> = await response.json();

    if (result.status === 'success' && result.data) {
      return result.data;
    } else {
      console.error('Failed to get event details:', result.message);
      return null;
    }
  } catch (error) {
    console.error('Error fetching event details:', error);
    return null;
  }
}
