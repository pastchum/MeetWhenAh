"use client";
import React, { useState, useEffect } from "react";
import WeekCalendar from "../../components/dragselector/WeekCalendar";
import { addDays, format, parse, startOfWeek } from "date-fns";
import { getEvent, EventDetails } from "app/utils/events_utils";

// Interface for aggregated time periods
interface TimePeriod {
  start: number; // minutes from midnight
  end: number; // minutes from midnight
}

export default function DragSelectorPage() {
  const [eventDetails, setEventDetails] = useState<EventDetails>({
    event_id: "",
    event_name: "",
    event_description: "",
    event_type: "",
    start_date: "",
    end_date: "",
    start_hour: "",
    end_hour: "",
    creator: "",
    created_at: "",
  });
  const [startDate, setStartDate] = useState<Date>(new Date());
  const [numDays, setNumDays] = useState<number>(7);
  const [selectionData, setSelectionData] = useState<Map<string, Set<number>>>(
    new Map()
  );
  const [username, setUsername] = useState<string>(""); // Default username
  const [eventId, setEventId] = useState<string>("");

  // Parse URL parameters
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);

    // Set event_id from URL parameters
    const urlEventId = urlParams.get("event_id");
    if (urlEventId) {
      setEventId(urlEventId);
    }

    // Try to get username from URL or use a default
    const urlUsername = urlParams.get("username");
    if (urlUsername) {
      setUsername(urlUsername);
    }
  }, []);

  //get event details
  useEffect(() => {
    const getEventDetails = async () => {
      if (!eventId) return;
      const eventDetails = await getEvent(eventId);
      if (eventDetails) {
        setEventDetails(eventDetails);
        setStartDate(new Date(eventDetails.start_date));
        setNumDays(
          Math.ceil(
            (new Date(eventDetails.end_date).getTime() -
              new Date(eventDetails.start_date).getTime()) /
              (1000 * 3600 * 24)
          )
        );
      }
    };
    getEventDetails();
  }, [eventId]);

  // Navigate to this week
  const navigateToThisWeek = () => {
    setStartDate(startOfWeek(new Date(), { weekStartsOn: 1 }));
  };

  // Handle previous/next week
  const navigatePreviousWeek = () => {
    setStartDate((prev) => addDays(prev, -numDays));
  };

  const navigateNextWeek = () => {
    setStartDate((prev) => addDays(prev, numDays));
  };

  // Format minutes as HH:MM
  const formatTime = (minutes: number): string => {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return `${hours.toString().padStart(2, "0")}:${mins
      .toString()
      .padStart(2, "0")}`;
  };

  // Aggregate consecutive time slots into periods
  const aggregateTimePeriods = (timeSet: Set<number>): TimePeriod[] => {
    if (timeSet.size === 0) return [];

    // Convert set to sorted array
    const times = Array.from(timeSet).sort((a, b) => a - b);

    const periods: TimePeriod[] = [];
    let currentPeriod: TimePeriod = {
      start: times[0],
      end: times[0] + 30, // Each slot is 30 minutes
    };

    // Group consecutive time slots
    for (let i = 1; i < times.length; i++) {
      const time = times[i];
      // If this time slot continues the current period (30 min increments)
      if (time === currentPeriod.end) {
        currentPeriod.end = time + 30;
      } else {
        // Save current period and start a new one
        periods.push({ ...currentPeriod });
        currentPeriod = {
          start: time,
          end: time + 30,
        };
      }
    }

    // Add the last period
    periods.push(currentPeriod);

    return periods;
  };

  // Format selection data for display
  const formatSelectionSummary = () => {
    const days = Array.from(selectionData.keys()).sort();

    return (
      <div>
        {days.map((day) => {
          const displayDate = format(
            parse(day, "yyyy-MM-dd", new Date()),
            "EEE, MMM d"
          );
          const periods = aggregateTimePeriods(
            selectionData.get(day) || new Set()
          );

          return (
            <div key={day} className="mb-2">
              <div className="font-semibold">{displayDate}</div>
              <ul className="ml-4">
                {periods.map((period, idx) => (
                  <li key={idx}>
                    {formatTime(period.start)} - {formatTime(period.end)}
                  </li>
                ))}
              </ul>
            </div>
          );
        })}
      </div>
    );
  };

  return (
    <div className="container mx-auto p-4">
      <div className="flex items-center mb-4">
        <h1 className="text-2xl font-bold">Weekly Availability Selector</h1>
        <span className="ml-4 text-sm px-3 py-1 bg-white rounded shadow-sm text-gray-600">
          Click on a day header to select the entire day, or drag across time
          slots to select specific periods.
        </span>
      </div>
      {eventDetails.event_name && (
        <div className="text-2xl font-bold">{eventDetails.event_name}</div>
      )}

      {username && (
        <div className="mb-2 text-sm text-gray-500">
          Setting availability for: {username}
        </div>
      )}

      <div className="mb-4 flex justify-between items-center">
        <button
          onClick={navigatePreviousWeek}
          className="px-4 py-2 bg-gray-200 hover:bg-gray-300 rounded"
        >
          Previous Week
        </button>

        <button
          onClick={navigateToThisWeek}
          className="px-4 py-2 bg-blue-500 text-white hover:bg-blue-600 rounded"
        >
          This Week
        </button>

        <button
          onClick={navigateNextWeek}
          className="px-4 py-2 bg-gray-200 hover:bg-gray-300 rounded"
        >
          Next Week
        </button>
      </div>

      <div className="bg-white rounded-lg shadow-md">
        <WeekCalendar
          startDate={startDate}
          numDays={numDays}
          username={username}
          eventId={eventId}
          onSelectionChange={setSelectionData}
        />
      </div>

      <div className="mt-4">
        <h2 className="text-xl font-semibold mb-2">Selected Times</h2>
        <div className="bg-gray-100 p-4 rounded text-gray-800 h-48 overflow-y-auto">
          {selectionData.size > 0 ? (
            formatSelectionSummary()
          ) : (
            <div className="text-gray-600 italic">
              No times selected. Click on a day header to select the entire day,
              or drag across time slots to select specific periods.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
