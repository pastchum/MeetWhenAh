"use client";
import React, { useState, useEffect } from "react";
import WeekCalendar from "../../components/dragselector/WeekCalendar";
import { addDays, format, parse, startOfWeek } from "date-fns";
import { EventData } from "@/utils/event_service";
import { AvailabilityData } from "@/utils/availability_service";
import { fetchEventFromAPI } from "@/routes/events_routes";
import { fetchUserAvailabilityFromAPI } from "@/routes/availability_routes";
import {
  fetchUserDataFromUsername,
  fetchUserDataFromId,
  addUserToDatabase,
} from "@/routes/user_routes";
import { useTelegramViewport } from "@/hooks/useTelegramViewport";

// Interface for aggregated time periods
interface TimePeriod {
  start: number; // minutes from midnight
  end: number; // minutes from midnight
}

export default function DragSelectorPage() {
  // Get viewport dimensions from Telegram Web App
  const viewport = useTelegramViewport();
  
  const [eventDetails, setEventDetails] = useState<EventData>({
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
    min_participants: 0,
    min_duration_blocks: 0,
    max_duration_blocks: 0,
  });
  const [startDate, setStartDate] = useState<Date>(new Date());
  const [endDate, setEndDate] = useState<Date>(new Date());
  const [numDays, setNumDays] = useState<number>(7);
  const [totalEventDays, setTotalEventDays] = useState<number>(7);
  const [currentRangeStart, setCurrentRangeStart] = useState<Date>(new Date());
  const [selectionData, setSelectionData] = useState<Set<string>>(new Set());
  const [teleId, setTeleId] = useState<string>("");
  const [username, setUsername] = useState<string>(""); // Default username
  const [userUuid, setUserUuid] = useState<string>("");
  const [eventId, setEventId] = useState<string>("");

  // Parse URL parameters and get user data from username or telegram id
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);

    if (window.Telegram.WebApp.initDataUnsafe.user) {
      const telegramId = window.Telegram.WebApp.initDataUnsafe.user.id;
      setTeleId(telegramId.toString());
    }
    // disable vertical swipes
    if (window.Telegram.WebApp) {
      window.Telegram.WebApp.disableVerticalSwipes();
    }

    // Set event_id from URL parameters
    const urlEventId = urlParams.get("event_id");
    if (urlEventId) {
      setEventId(urlEventId);
    }

    // Try to get username from URL or use a default
    const urlUsername = urlParams.get("username");
    if (urlUsername) {
      setUsername(urlUsername);
      fetchUserUuidFromUsername(urlUsername);
    }
  }, []);

  //get event details
  useEffect(() => {
    const getEventDetails = async () => {
      if (!eventId) return;
      const eventDetails = await fetchEventFromAPI(eventId);
      if (eventDetails) {
        console.log(eventDetails);
        setEventDetails(eventDetails);
        setStartDate(new Date(eventDetails.start_date));
        setEndDate(new Date(eventDetails.end_date));
        // Calculate event duration in days
        const eventStart = new Date(eventDetails.start_date);
        console.log("eventStart", eventDetails.start_date);
        console.log("eventStart", eventStart);
        const eventEnd = new Date(eventDetails.end_date);
        const totalDays = Math.ceil(
          (eventEnd.getTime() - eventStart.getTime()) / (1000 * 3600 * 24) + 1
        );

        setTotalEventDays(totalDays);
        setCurrentRangeStart(eventStart);

        // If event is less than 7 days, show full range. Otherwise, show 7 days
        setNumDays(Math.min(totalDays, 7));
      }
    };
    getEventDetails();
  }, [eventId]);

  // get user uuid from telegram id
  useEffect(() => {
    if (!teleId) return;
    const fetchUserUuidFromTeleId = async () => {
      const userData = await fetchUserDataFromId(teleId.toString());
      if (userData) {
        setUserUuid(userData.uuid);
        setUsername(userData.tele_user);
      } else {
        // add user to database
        const telegramUser = window.Telegram.WebApp.initDataUnsafe.user;
        if (telegramUser) {
          const newUserData = {
            uuid: crypto.randomUUID(),
            tele_id: telegramUser.id.toString(),
            tele_user: telegramUser.username || "",
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
            initialised: true,
            callout_cleared: true,
            sleep_start_time: "00:00:00",
            sleep_end_time: "00:00:00",
            tmp_sleep_start: "00:00:00",
          };
          const newUser = await addUserToDatabase(newUserData);
          if (newUser) {
            setUserUuid(newUser.uuid);
            setUsername(newUser.tele_user);
            setTeleId(newUser.tele_id);
          }
        }
      }
    };
    fetchUserUuidFromTeleId();
  }, [teleId]);

  // function to get user uuid from username
  const fetchUserUuidFromUsername = async (username: string) => {
    const userData = await fetchUserDataFromUsername(username);
    if (userData) {
      setUserUuid(userData.uuid);
      setUsername(userData.tele_user);
      setTeleId(userData.tele_id);
    }
  };

  // get user availability
  useEffect(() => {
    if (!userUuid || !username || !teleId) return;
    const fetchUserAvailability = async () => {
      const availability = await fetchUserAvailabilityFromAPI(
        teleId.toString(),
        eventId
      );
      console.log(availability);
      if (availability) {
        // Convert availability blocks to ISO datetime strings
        const newSelectionData = new Set<string>();

        availability.forEach((block: AvailabilityData) => {
          try {
            const startDate = new Date(block.start_time);
            const endDate = new Date(block.end_time);

            if (isNaN(startDate.getTime()) || isNaN(endDate.getTime())) {
              console.error("Invalid date in availability block:", block);
              return;
            }

            // Add start time to selection data (normalized to local timezone)
            const normalizedStartTime = normalizeIsoDatetime(block.start_time);
            newSelectionData.add(normalizedStartTime);

            // If there are multiple 30-minute slots, add them too
            let currentTime = new Date(startDate);
            currentTime.setMinutes(currentTime.getMinutes() + 30);

            while (currentTime < endDate) {
              const timeString = normalizeIsoDatetime(
                currentTime.toISOString()
              );
              newSelectionData.add(timeString);
              currentTime.setMinutes(currentTime.getMinutes() + 30);
            }
          } catch (error) {
            console.error("Error processing availability block:", block, error);
          }
        });

        setSelectionData(newSelectionData);
      }
    };
    fetchUserAvailability();
  }, [userUuid, eventId, teleId, username]);

  // Navigate to the event's start date
  const navigateToEventStart = () => {
    if (eventDetails.start_date) {
      const eventStart = new Date(eventDetails.start_date);
      setStartDate(eventStart);
      setCurrentRangeStart(eventStart);
      setNumDays(Math.min(totalEventDays, 7));
    }
  };

  // Handle previous 7-day period
  const navigatePreviousPeriod = () => {
    setStartDate((prev) => {
      const newStart = addDays(prev, -7);
      // Don't go before the event start date
      if (newStart < new Date(eventDetails.start_date)) {
        return prev;
      }
      setCurrentRangeStart(newStart);
      return newStart;
    });
  };

  // Handle next 7-day period
  const navigateNextPeriod = () => {
    setStartDate((prev) => {
      const newStart = addDays(prev, 7);
      // Don't go beyond the event end date
      const eventEnd = new Date(eventDetails.end_date);
      if (newStart >= eventEnd) {
        return prev;
      }
      setCurrentRangeStart(newStart);
      return newStart;
    });
  };

  // Format minutes as HH:MM
  const formatTime = (minutes: number): string => {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return `${hours.toString().padStart(2, "0")}:${mins
      .toString()
      .padStart(2, "0")}`;
  };

  // Helper function to convert ISO datetime to day and time
  const getDayAndTimeFromIso = (
    isoString: string
  ): { day: string; time: number } => {
    const date = new Date(isoString);
    const day = format(date, "yyyy-MM-dd");
    const time = date.getHours() * 60 + date.getMinutes();
    return { day, time };
  };

  // Helper function to normalize ISO datetime to local timezone for comparison
  const normalizeIsoDatetime = (isoString: string): string => {
    const date = new Date(isoString);
    const year = date.getFullYear();
    const month = date.getMonth() + 1;
    const day = date.getDate();
    const hours = date.getHours();
    const minutes = date.getMinutes();

    // Recreate the date in local timezone to ensure consistent timezone handling
    const localDate = new Date(year, month - 1, day, hours, minutes);
    return localDate.toISOString();
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
    // Group ISO datetimes by day
    const dayGroups = new Map<string, Set<number>>();

    selectionData.forEach((isoString) => {
      const { day, time } = getDayAndTimeFromIso(isoString);
      if (!dayGroups.has(day)) {
        dayGroups.set(day, new Set<number>());
      }
      dayGroups.get(day)!.add(time);
    });

    const days = Array.from(dayGroups.keys()).sort();

    return (
      <div>
        {days.map((day) => {
          let displayDate;
          try {
            // Try to parse the date string safely
            const parsedDate = parse(day, "yyyy-MM-dd", new Date());
            // Check if the parsed date is valid
            if (isNaN(parsedDate.getTime())) {
              throw new Error("Invalid date");
            }
            displayDate = format(parsedDate, "EEE, MMM d");
          } catch (error) {
            // Fallback: try to create a date directly from the string
            try {
              const fallbackDate = new Date(day);
              if (isNaN(fallbackDate.getTime())) {
                displayDate = day; // Use the original string if all else fails
              } else {
                displayDate = format(fallbackDate, "EEE, MMM d");
              }
            } catch {
              displayDate = day; // Use the original string if all else fails
            }
          }

          const periods = aggregateTimePeriods(dayGroups.get(day) || new Set());

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
    <div 
      className="flex flex-col w-full"
      style={{ 
        height: `${viewport.totalHeight}px`,
        transform: 'translateZ(0)' // Create new stacking context
      }}
    >
      {/* Fixed Header Section */}
      <div className="flex-shrink-0 p-4 bg-gray-900">
        {eventDetails.event_name && (
          <div className="text-2xl font-bold text-center text-slate-50">
            {eventDetails.event_name}
          </div>
        )}

        {username && (
          <div className="mb-2 text-sm text-gray-500">
            Setting availability for: {username}
          </div>
        )}

        <div className="mb-4 flex justify-between items-center">
          <button
            onClick={navigatePreviousPeriod}
            className="px-4 py-2 bg-gray-200 hover:bg-gray-300 rounded"
            disabled={startDate <= new Date(eventDetails.start_date)}
          >
            Previous 7 Days
          </button>

          <button
            onClick={navigateToEventStart}
            className="px-4 py-2 bg-blue-500 text-white hover:bg-blue-600 rounded"
          >
            Event Start
          </button>

          <button
            onClick={navigateNextPeriod}
            className="px-4 py-2 bg-gray-200 hover:bg-gray-300 rounded"
            disabled={addDays(startDate, 7) >= new Date(eventDetails.end_date)}
          >
            Next 7 Days
          </button>
        </div>
      </div>

      {/* Fixed Instructions */}
      <div className="flex-shrink-0 px-4 pb-4">
        <div className="flex items-center">
          <span className="text-sm px-3 py-1 bg-white rounded shadow-sm text-gray-600">
            Click on a day header to select the entire day, or drag across time
            slots to select specific periods.
          </span>
        </div>
      </div>

      {/* Scrollable WeekCalendar */}
      <div className="flex-1 px-4 overflow-hidden">
        <div 
          className="bg-white rounded-lg shadow-md h-full overflow-y-auto"
          style={{ transform: 'translateZ(0)' }}
        >
          <WeekCalendar
            startDate={startDate}
            endDate={endDate}
            numDays={numDays}
            tele_id={teleId}
            eventId={eventId}
            userUuid={userUuid}
            onSelectionChange={setSelectionData}
          />
        </div>
      </div>

      {/* Fixed Selected Times Section */}
      <div className="flex-shrink-0 p-4 bg-gray-900">
        <h2 className="text-xl font-semibold mb-2 text-white">Selected Times</h2>
        <div className="bg-gray-100 p-4 rounded text-gray-800 h-32 overflow-y-auto">
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

      {/* Debug Info (only in development) */}
      {process.env.NODE_ENV === 'development' && (
        <div className="fixed top-2 right-2 bg-black bg-opacity-75 text-white text-xs p-2 rounded z-50">
          <div>Platform: {viewport.platform}</div>
          <div>Total: {viewport.totalHeight}px</div>
          <div>Window: {typeof window !== 'undefined' ? window.innerHeight : 'N/A'}px</div>
          <div>Flex Layout: Active</div>
        </div>
      )}
    </div>
  );
}
