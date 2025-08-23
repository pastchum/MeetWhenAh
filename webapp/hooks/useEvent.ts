import { useEffect, useState } from "react";
import { Event } from "@/types/Event";

// request details for confirming an event
type confirmEventRequestDetails = {
    event_id: string;
    start_time: string;
    end_time: string;
}

/**
 * useEvent hook
 * 
 * This hook is used to fetch an event by its ID
 * 
 * @param event_id - The ID of the event to fetch
 * @returns {Object} - An object containing the event, loading state, error state, and functions to create, delete, and update events
 * 
 * @example
 * 
 */
const useEvent = (event_id: string) => {
    const [event, setEvent] = useState<Event | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<Error | null>(null);

    useEffect(() => {
        const fetchEvent = async () => {
            const response = await fetch(`/api/event/${event_id}`);
            const data = await response.json();
            setEvent(data);
        }
    }, [event_id]);

    const createEvent = async (event: Event) => {
        try {
          const response = await fetch(`/api/event/create`, {
            method: "POST",
            body: JSON.stringify(event),
          });
          if (!response.ok) {
            throw new Error("Failed to create event");
          }
          const data = await response.json();
          setEvent(data);   
        }
        catch (error) {
          setError(error as Error);
        }
      };
    
      const deleteEvent = async (eventId: string) => {
        try {
          const response = await fetch(`/api/event/delete/${eventId}`, {
            method: "DELETE",
          });
          if (!response.ok) {
            throw new Error("Failed to delete event");
          }
          const data = await response.json();
          setEvent(null);
        }
        catch (error) {
          setError(error as Error);
        }
        finally {
          setLoading(false);
        }
      };
    
      const updateEvent = async (event: Event) => {
        try {
          const response = await fetch(`/api/event/update/${event.event_id}`, {
            method: "PUT",
            body: JSON.stringify(event),
          });
          if (!response.ok) {
            throw new Error("Failed to update event");
          }
          const data = await response.json();
          setEvent(data);
        }
        catch (error) {
          setError(error as Error);
        }
        finally {
          setLoading(false);
        }
      };
    
      const confirmEvent = async (eventDetails: confirmEventRequestDetails) => {
        try {
          const response = await fetch(`/api/event/confirm`, {
            method: "POST",
            body: JSON.stringify(eventDetails),
          });
          if (!response.ok) {
            throw new Error("Failed to confirm event");
          }
          const data = await response.json();
          setEvent(data);
        }
        catch (error) {
          setError(error as Error);
        }
        finally {
          setLoading(false);
        }
      }

    return { event, loading, error, createEvent, deleteEvent, updateEvent, confirmEvent };
}

export default useEvent;