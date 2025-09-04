import { useEffect, useMemo, useState } from "react";
import useUser from "./useUser";
import { Event, ConfirmedEvent } from "../types/Event";
import User from "../types/User";

/**
 * useUserEvents hook 
 * 
 * This hook is used to fetch user events and confirmed events
 * 
 * @returns {Object} - An object containing the user events, confirmed events, unconfirmed events, loading state, error state, and functions to create, delete, and update events
 * 
 */ 
const useUserEvents = (tele_id?: string) => {
  const [events, setEvents] = useState<Event[]>([]);
  const [confirmedEvents, setConfirmedEvents] = useState<ConfirmedEvent[]>([]);
  const [unconfirmedEvents, setUnconfirmedEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const { user } = useUser(tele_id);

  useEffect(() => {
    const fetchUserEvents = async () => {
      try {
        const response = await fetch(`/api/user/events/${user?.tele_id}`);
        if (!response.ok) {
          throw new Error("Failed to fetch user events");
        }
        const data = await response.json();
        console.log("data: ", data);
        setEvents(data);
      }
      catch (error) {
        setError(error as Error);
      }
      finally {
        setLoading(false);
      }
    };
    fetchUserEvents();
  }, [user]);

  useEffect(() => {
    const fetchConfirmedEvents = async () => {
      try {
        const response = await fetch(`/api/user/confirmed-events/${user?.tele_id}`);
        if (!response.ok) {
          throw new Error("Failed to fetch confirmed events");
        }
        const data = await response.json();
        return data.data;
      }
      catch (error) {
        setError(error as Error);
      }
      finally {
        setLoading(false);
      }
    };
    fetchConfirmedEvents();

    // append confirmed event details to confirmed events
    if (Array.isArray(events)) {
      events.forEach((event, index) => {
      if (confirmedEvents.find((e) => e.event_id === event.event_id)) {
        const e = confirmedEvents.find((e) => e.event_id === event.event_id);
        const eventData = { ...event, ...e };
        setConfirmedEvents([...confirmedEvents, eventData as ConfirmedEvent]);
      } else {
        if (!unconfirmedEvents.includes(event)) {
            setUnconfirmedEvents([...unconfirmedEvents, event]);
        }
      }
    })
    }

  }, [user, events]);

  const confirmedEventsToShow = useMemo(() => {
    return confirmedEvents.filter((event) => event.event_id !== null);
  }, [confirmedEvents]);

  const unconfirmedEventsToShow = useMemo(() => { 
    return unconfirmedEvents.filter((event) => event.event_id !== null);
  }, [unconfirmedEvents]);

  return { 
    events, 
    confirmedEvents: confirmedEventsToShow, 
    unconfirmedEvents: unconfirmedEventsToShow, 
    loading, 
    error 
  };
};

export default useUserEvents;