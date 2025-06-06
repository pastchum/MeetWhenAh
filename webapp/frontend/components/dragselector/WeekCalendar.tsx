"use client";

import React, { useState, useRef, useEffect, useCallback } from "react";
import DayHeader from "./DayHeader";
import TimeColumn from "./TimeColumn";
import TimeGrid from "./TimeGrid";
import { format, addDays, startOfWeek, parse } from "date-fns";

interface WeekCalendarProps {
  startDate?: Date;
  numDays?: number;
  username?: string;
  eventId?: string;
  onSelectionChange?: (selectedSlots: Map<string, Set<number>>) => void;
}

const WeekCalendar: React.FC<WeekCalendarProps> = ({
  startDate = new Date(),
  numDays = 7,
  username = "",
  eventId = "",
  onSelectionChange,
}) => {
  // Selected slots: Map<dayKey, Set<timeInMinutes>>
  const [selectedSlots, setSelectedSlots] = useState<Map<string, Set<number>>>(
    new Map()
  );

  // Drag state
  const [isDragging, setIsDragging] = useState(false);
  const [dragOperation, setDragOperation] = useState<"select" | "deselect">(
    "select"
  );
  const [lastSlot, setLastSlot] = useState<{
    day: string;
    time: number;
  } | null>(null);

  // Loading state
  const [isLoading, setIsLoading] = useState(false);
  const [syncedWithBackend, setSyncedWithBackend] = useState(false);

  // Generate days array
  const weekStart = startOfWeek(startDate, { weekStartsOn: 1 }); // Week starts Monday
  const days = Array.from({ length: numDays }, (_, i) => addDays(weekStart, i));

  // Time slots (every 30 minutes from 00:00 to 23:30)
  const timeSlots = Array.from({ length: 48 }, (_, i) => i * 30);

  // Container ref for position calculations
  const containerRef = useRef<HTMLDivElement>(null);

  // Throttle backend updates
  const [pendingSync, setPendingSync] = useState(false);
  const syncTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Fetch user availability from backend
  const fetchUserAvailability = useCallback(async () => {
    if (!username || !eventId) return;

    setIsLoading(true);
    try {
      const response = await fetch(
        `/api/availability/${encodeURIComponent(username)}/${encodeURIComponent(
          eventId
        )}`
      );
      const data = await response.json();

      if (data.status === "success" && Array.isArray(data.data)) {
        // Convert backend data to our format
        const newSelectedSlots = new Map<string, Set<number>>();

        data.data.forEach((slot: { date: string; time: string }) => {
          const dayKey = slot.date;
          const timeMinutes =
            parseInt(slot.time.slice(0, 2)) * 60 + parseInt(slot.time.slice(2));

          if (!newSelectedSlots.has(dayKey)) {
            newSelectedSlots.set(dayKey, new Set<number>());
          }

          newSelectedSlots.get(dayKey)?.add(timeMinutes);
        });

        setSelectedSlots(newSelectedSlots);
      }
    } catch (error) {
      console.error("Error fetching user availability:", error);
    } finally {
      setIsLoading(false);
      setSyncedWithBackend(true);
    }
  }, [username, eventId]);

  // Sync to backend
  const syncToBackend = useCallback(async () => {
    if (!username || !eventId || !syncedWithBackend) return;

    try {
      // Convert our data format to backend format
      const availabilityData: { date: string; time: string }[] = [];

      selectedSlots.forEach((timeSet, dayKey) => {
        timeSet.forEach((timeMinutes) => {
          const hours = Math.floor(timeMinutes / 60);
          const minutes = timeMinutes % 60;
          const timeString = `${hours.toString().padStart(2, "0")}${minutes
            .toString()
            .padStart(2, "0")}`;

          availabilityData.push({
            date: dayKey,
            time: timeString,
          });
        });
      });

      // Send to backend
      await fetch("/api/availability", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          username,
          event_id: eventId,
          availability_data: availabilityData,
        }),
      });

      console.log("Availability synced with backend");
    } catch (error) {
      console.error("Error syncing to backend:", error);
    } finally {
      setPendingSync(false);
    }
  }, [username, eventId, selectedSlots, syncedWithBackend]);

  // Load initial data
  useEffect(() => {
    fetchUserAvailability();
  }, [fetchUserAvailability]);

  // Throttled syncing to backend
  useEffect(() => {
    if (pendingSync && syncedWithBackend) {
      if (syncTimeoutRef.current) {
        clearTimeout(syncTimeoutRef.current);
      }

      syncTimeoutRef.current = setTimeout(() => {
        syncToBackend();
      }, 2000); // Wait 2 seconds before syncing to reduce API calls
    }

    return () => {
      if (syncTimeoutRef.current) {
        clearTimeout(syncTimeoutRef.current);
      }
    };
  }, [pendingSync, syncToBackend, syncedWithBackend]);

  // Load saved pattern or current availability if provided in URL query params
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);

    // Check for saved pattern
    const savedPattern = urlParams.get("saved_pattern");
    if (savedPattern) {
      try {
        const patternData = JSON.parse(savedPattern);

        // Get current day of week
        const newSelectedSlots = new Map<string, Set<number>>(selectedSlots);

        days.forEach((day) => {
          const dayOfWeek = format(day, "EEEE"); // Monday, Tuesday, etc.
          const dayKey = format(day, "yyyy-MM-dd");

          if (patternData[dayOfWeek] && Array.isArray(patternData[dayOfWeek])) {
            if (!newSelectedSlots.has(dayKey)) {
              newSelectedSlots.set(dayKey, new Set<number>());
            }

            patternData[dayOfWeek].forEach((timeString: string) => {
              const hours = parseInt(timeString.slice(0, 2));
              const minutes = parseInt(timeString.slice(2));
              newSelectedSlots.get(dayKey)?.add(hours * 60 + minutes);
            });
          }
        });

        setSelectedSlots(newSelectedSlots);
      } catch (error) {
        console.error("Error parsing saved pattern:", error);
      }
    }

    // Check for current availability
    const currentAvailability = urlParams.get("current_availability");
    if (currentAvailability) {
      try {
        const availabilityData = JSON.parse(currentAvailability);

        if (Array.isArray(availabilityData)) {
          const newSelectedSlots = new Map<string, Set<number>>();

          availabilityData.forEach((slot: { date: string; time: string }) => {
            const dayKey = slot.date;
            const timeMinutes =
              parseInt(slot.time.slice(0, 2)) * 60 +
              parseInt(slot.time.slice(2));

            if (!newSelectedSlots.has(dayKey)) {
              newSelectedSlots.set(dayKey, new Set<number>());
            }

            newSelectedSlots.get(dayKey)?.add(timeMinutes);
          });

          setSelectedSlots(newSelectedSlots);
        }
      } catch (error) {
        console.error("Error parsing current availability:", error);
      }
    }
  }, [days, selectedSlots]);

  // Handle day header click - select whole day
  const handleSelectWholeDay = useCallback(
    (date: Date) => {
      const dayKey = format(date, "yyyy-MM-dd");

      // Check if any slots for this day are already selected
      const isAnySlotSelected =
        selectedSlots.has(dayKey) && selectedSlots.get(dayKey)!.size > 0;

      setSelectedSlots((prev) => {
        const newMap = new Map(prev);

        if (isAnySlotSelected) {
          // If any slots are selected, deselect the whole day
          newMap.delete(dayKey);
        } else {
          // Select all time slots for the day
          const allTimes = new Set<number>();
          timeSlots.forEach((time) => allTimes.add(time));
          newMap.set(dayKey, allTimes);
        }

        return newMap;
      });

      // Mark for syncing to backend
      setPendingSync(true);
    },
    [selectedSlots, timeSlots]
  );

  // Handle drag start
  const handleDragStart = useCallback(
    (day: string, time: number, isSelected: boolean) => {
      setIsDragging(true);
      setDragOperation(isSelected ? "deselect" : "select");
      setLastSlot({ day, time });

      // Update initial selection
      updateSelection(day, time, isSelected ? "deselect" : "select");
    },
    []
  );

  // Handle drag over time slot
  const handleDragOver = useCallback(
    (day: string, time: number) => {
      if (!isDragging || !lastSlot) return;

      // If we moved to a new slot
      if (day !== lastSlot.day || time !== lastSlot.time) {
        updateSelection(day, time, dragOperation);
        setLastSlot({ day, time });
      }
    },
    [isDragging, lastSlot, dragOperation]
  );

  // Handle drag end
  const handleDragEnd = useCallback(() => {
    setIsDragging(false);
    setLastSlot(null);

    // Mark for syncing to backend
    setPendingSync(true);
  }, []);

  // Update selection based on drag operation
  const updateSelection = (
    day: string,
    time: number,
    operation: "select" | "deselect"
  ) => {
    setSelectedSlots((prev) => {
      const newMap = new Map(prev);

      if (operation === "select") {
        // If selecting, add the time to the day's set
        if (!newMap.has(day)) {
          newMap.set(day, new Set<number>());
        }
        newMap.get(day)?.add(time);
      } else {
        // If deselecting, remove the time from the day's set
        newMap.get(day)?.delete(time);
        // Remove day entirely if no times are selected
        if (newMap.get(day)?.size === 0) {
          newMap.delete(day);
        }
      }

      return newMap;
    });
  };

  // Notify parent about selection changes
  useEffect(() => {
    onSelectionChange?.(selectedSlots);
  }, [selectedSlots, onSelectionChange]);

  // Prevent text selection during dragging
  useEffect(() => {
    const preventDefault = (e: Event) => {
      if (isDragging) {
        e.preventDefault();
      }
    };

    document.addEventListener("selectstart", preventDefault);
    return () => {
      document.removeEventListener("selectstart", preventDefault);
    };
  }, [isDragging]);

  // Handle drag end when mouse is released anywhere in the document
  useEffect(() => {
    const handleMouseUp = () => {
      if (isDragging) {
        handleDragEnd();
      }
    };

    document.addEventListener("mouseup", handleMouseUp);
    document.addEventListener("touchend", handleMouseUp);

    return () => {
      document.removeEventListener("mouseup", handleMouseUp);
      document.removeEventListener("touchend", handleMouseUp);
    };
  }, [isDragging, handleDragEnd]);

  return (
    <div
      className="relative flex flex-col overflow-auto border border-gray-200 rounded-lg"
      style={{ userSelect: "none" }}
      ref={containerRef}
    >
      {isLoading && (
        <div className="absolute inset-0 flex items-center justify-center bg-white bg-opacity-70 z-20">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
        </div>
      )}

      {/* Day headers row */}
      <div className="sticky top-0 z-10 flex bg-white">
        <div className="w-16 flex-shrink-0 border-r border-b border-gray-200" />
        <div className="flex-1 flex">
          {days.map((day, idx) => (
            <DayHeader
              key={idx}
              date={day}
              width={`${100 / numDays}%`}
              onSelectDay={handleSelectWholeDay}
            />
          ))}
        </div>
      </div>

      {/* Calendar body */}
      <div className="flex flex-1">
        {/* Time labels column */}
        <TimeColumn timeSlots={timeSlots} />

        {/* Grid of time slots */}
        <TimeGrid
          days={days}
          timeSlots={timeSlots}
          selectedSlots={selectedSlots}
          isDragging={isDragging}
          onDragStart={handleDragStart}
          onDragOver={handleDragOver}
          onDragEnd={handleDragEnd}
        />
      </div>
    </div>
  );
};

export default WeekCalendar;
