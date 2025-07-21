import { AvailabilityData } from "@/utils/availability_service";

export async function fetchUserAvailabilityFromAPI(tele_id: string, event_id: string) : Promise<AvailabilityData[] | null> {
    try {
        const response = await fetch(`/api/availability/get/${event_id}/${tele_id}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        });
        if (!response.ok) {
            throw new Error('Failed to fetch availability');
        }
        const result = await response.json();
        return result.data || []; // Return empty array if no availability found
    } catch (error) {
        console.error('Error fetching availability:', error);
        return null;
    }
}

export async function fetchEventAvailabilityFromAPI(event_id: string): Promise<Record<string, AvailabilityData[]> | null> {
    try {
        const response = await fetch(`/api/availability/event/${event_id}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        });
        if (!response.ok) {
            throw new Error('Failed to fetch event availability');
        }
        const result = await response.json();
        return result.data || {}; // Return empty object if no availability found
    } catch (error) {
        console.error('Error fetching event availability:', error);
        return null;
    }
}

export async function updateUserAvailabilityToAPI(tele_id: string, event_id: string, availability_data: AvailabilityData[]) {
    try {
        const response = await fetch(`/api/availability/save`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                tele_id,
                event_id,
                availability_data
            }),
        });
        if (!response.ok) {
            throw new Error('Failed to update availability');
        }
        const result = await response.json();
        return result.data || null;
    } catch (error) {
        console.error('Error updating availability:', error);
        return null;
    }
}