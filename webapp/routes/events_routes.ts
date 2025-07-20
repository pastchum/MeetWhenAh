import { EventData } from "@/utils/event_service";

export async function fetchEventFromAPI(event_id: string) : Promise<EventData | null> {
    try {
        const response = await fetch(`/api/event/${event_id}`);
        if (!response.ok) {
            throw new Error('Failed to fetch event');
        }
        const result = await response.json();
        return result.data || null;
    } catch (error) {
        console.error('Error fetching event:', error);
        return null;
    }
}