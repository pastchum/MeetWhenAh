"use client";

import React, { useState, useRef, useEffect, useCallback } from "react";
import DayHeader from "./DayHeader";
import TimeColumn from "./TimeColumn";
import TimeGrid from "./TimeGrid";
import { format, addDays, startOfWeek, parse, addMinutes } from "date-fns";
import {
  fetchUserAvailabilityFromAPI,
  updateUserAvailabilityToAPI,
} from "@/routes/availability_routes";
import { AvailabilityData } from "@/utils/availability_service";
import { 
  getUtcDatetime, 
  getLocalDayAndTime,
  isSlotSelected 
} from "@/lib/datetime-utils";

interface WeekCalendarProps {
  startDate?: Date;
  endDate?: Date;
  numDays?: number;
  tele_id?: string;
  eventId?: string;
  userUuid?: string;
  onSelectionChange?: (selectedSlots: Set<string>) => void;
}

const WeekCalendar: React.FC<WeekCalendarProps> = ({
  startDate = new Date(),
  endDate = new Date(),
  numDays = 7,
  tele_id = "",
  eventId = "",
  userUuid = "",
  onSelectionChange,
}) => {
  // Selected slots: Set<ISO datetime string>
  const [selectedSlots, setSelectedSlots] = useState<Set<string>>(new Set());

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
  const days = Array.from({ length: numDays }, (_, i) => addDays(startDate, i));

  // Time slots (every 30 minutes from 00:00 to 23:30)
  const timeSlots = Array.from({ length: 48 }, (_, i) => i * 30);

  // Container ref for position calculations
  const containerRef = useRef<HTMLDivElement>(null);

  // Throttle backend updates
  const [pendingSync, setPendingSync] = useState(false);
  const syncTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Update selection based on drag operation
  const updateSelection = useCallback(
    (day: string, time: number, operation: "select" | "deselect") => {
      setSelectedSlots((prev) => {
        const newSet = new Set(prev);
        const utcDatetime = getUtcDatetime(day, time);

        if (operation === "select") {
          newSet.add(utcDatetime);
        } else {
          newSet.delete(utcDatetime);
        }

        return newSet;
      });
    },
    []
  );

  // Fetch user availability from backend
  const fetchUserAvailability = useCallback(async () => {
    if (!tele_id || !eventId) return;

    setIsLoading(true);
    try {
      const data = await fetchUserAvailabilityFromAPI(tele_id, eventId);
      if (!data) return;

      const newSelectedSlots = new Set<string>();
      console.log(data);
      data.forEach((slot: AvailabilityData) => {
        try {
          const startDate = new Date(slot.start_time);
          const endDate = new Date(slot.end_time);

          if (isNaN(startDate.getTime()) || isNaN(endDate.getTime())) {
            console.error("Invalid date in availability block:", slot);
            return;
          }

          // Add start time to selection data (normalize to UTC ISO format)
          newSelectedSlots.add(startDate.toISOString());

          // If there are multiple 30-minute slots, add them too
          let currentTime = new Date(startDate);
          currentTime.setMinutes(currentTime.getMinutes() + 30);

          while (currentTime < endDate) {
            const timeString = currentTime.toISOString();
            newSelectedSlots.add(timeString);
            currentTime.setMinutes(currentTime.getMinutes() + 30);
          }
        } catch (error) {
          console.error("Error processing availability block:", slot, error);
        }
      });

      setSelectedSlots(newSelectedSlots);
    } catch (error) {
      console.error("Error fetching user availability:", error);
    } finally {
      setIsLoading(false);
      setSyncedWithBackend(true);
    }
  }, [tele_id, eventId]);

  // Sync to backend
  const syncToBackend = useCallback(async () => {
    if (!tele_id || !eventId || !syncedWithBackend) return;

    try {
      // Convert our data format to backend format
      const availabilityData: AvailabilityData[] = [];

      // Group consecutive time slots into blocks
      const sortedSlots = Array.from(selectedSlots).sort();

      for (let i = 0; i < sortedSlots.length; i++) {
        const startTime = sortedSlots[i];
        let endTime = startTime;

        // Find consecutive slots (30-minute intervals)
        while (i + 1 < sortedSlots.length) {
          const currentDate = new Date(startTime);
          const nextDate = new Date(sortedSlots[i + 1]);
          const timeDiff = nextDate.getTime() - currentDate.getTime();

          // If next slot is exactly 30 minutes after current, it's consecutive
          if (timeDiff === 30 * 60 * 1000) {
            endTime = sortedSlots[i + 1];
            i++;
          } else {
            break;
          }
        }

        // Add 30 minutes to end time to make it exclusive
        const endDateTime = new Date(endTime);
        endDateTime.setMinutes(endDateTime.getMinutes() + 30);

        const data: AvailabilityData = {
          user_uuid: userUuid,
          event_id: eventId,
          start_time: startTime,
          end_time: endDateTime.toISOString(),
        };
        availabilityData.push(data);
      }
      updateUserAvailabilityToAPI(tele_id, eventId, availabilityData);

      console.log("Availability synced with backend");
    } catch (error) {
      console.error("Error syncing to backend:", error);
    } finally {
      setPendingSync(false);
    }
  }, [tele_id, eventId, selectedSlots, syncedWithBackend, userUuid]);

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

        const newSelectedSlots = new Set<string>();

        days.forEach((day) => {
          const dayOfWeek = format(day, "EEEE"); // Monday, Tuesday, etc.
          const dayKey = format(day, "yyyy-MM-dd");

          if (patternData[dayOfWeek] && Array.isArray(patternData[dayOfWeek])) {
            patternData[dayOfWeek].forEach((timeString: string) => {
              const hours = parseInt(timeString.slice(0, 2));
              const minutes = parseInt(timeString.slice(2));
              const utcDatetime = getUtcDatetime(dayKey, hours * 60 + minutes);
              newSelectedSlots.add(utcDatetime);
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
          const newSelectedSlots = new Set<string>();

          availabilityData.forEach((slot: { date: string; time: string }) => {
            const dayKey = slot.date;
            const timeMinutes =
              parseInt(slot.time.slice(0, 2)) * 60 +
              parseInt(slot.time.slice(2));
            const utcDatetime = getUtcDatetime(dayKey, timeMinutes);
            newSelectedSlots.add(utcDatetime);
          });

          setSelectedSlots(newSelectedSlots);
        }
      } catch (error) {
        console.error("Error parsing current availability:", error);
      }
    }
  }, [days]);

  // Handle day header click - select whole day
  const handleSelectWholeDay = useCallback(
    (date: Date) => {
      console.log('[WeekCalendar] handleSelectWholeDay called with date:', date);
      
      // Don't allow selection if date is after end date
      if (endDate && date > endDate) {
        console.log('[WeekCalendar] Date after end date, returning');
        return;
      }

      const dayKey = format(date, "yyyy-MM-dd");
      console.log('[WeekCalendar] Day key:', dayKey);

      // Check if any slots for this day are already selected
      const daySlots = Array.from(selectedSlots).filter((slot) => {
        const { day } = getLocalDayAndTime(slot);
        return day === dayKey;
      });

      const isAnySlotSelected = daySlots.length > 0;
      console.log('[WeekCalendar] Day slots already selected:', daySlots);
      console.log('[WeekCalendar] Is any slot selected:', isAnySlotSelected);

      setSelectedSlots((prev) => {
        console.log('[WeekCalendar] Previous selectedSlots:', Array.from(prev));
        const newSet = new Set(prev);

        if (isAnySlotSelected) {
          // If any slots are selected, deselect the whole day
          console.log('[WeekCalendar] Deselecting whole day');
          timeSlots.forEach((time) => {
            const utcDatetime = getUtcDatetime(dayKey, time);
            newSet.delete(utcDatetime);
          });
        } else {
          // Select all time slots for the day
          console.log('[WeekCalendar] Selecting all time slots for day');
          timeSlots.forEach((time) => {
            const utcDatetime = getUtcDatetime(dayKey, time);
            newSet.add(utcDatetime);
            console.log('[WeekCalendar] Added slot:', { dayKey, time, utcDatetime });
          });
        }

        console.log('[WeekCalendar] New selectedSlots:', Array.from(newSet));
        return newSet;
      });

      // Mark for syncing to backend
      setPendingSync(true);
    },
    [timeSlots, endDate]
  );

  // Handle drag start
  const handleDragStart = useCallback(
    (day: string, time: number, isSelected: boolean) => {
      console.log('[WeekCalendar] Drag start:', { day, time, isSelected });
      setIsDragging(true);
      setDragOperation(isSelected ? "deselect" : "select");
      setLastSlot({ day, time });

      // Update initial selection
      updateSelection(day, time, isSelected ? "deselect" : "select");
    },
    [updateSelection]
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
    [isDragging, lastSlot, dragOperation, updateSelection]
  );

  // Handle drag end
  const handleDragEnd = useCallback(() => {
    setIsDragging(false);
    setLastSlot(null);

    // Mark for syncing to backend
    setPendingSync(true);
  }, []);

  // Handle tap to toggle individual slot
  const handleTapToToggle = useCallback((day: string, time: number) => {
    const utcDatetime = getUtcDatetime(day, time);

    setSelectedSlots((prev) => {
      const newSet = new Set(prev);
      
      // Check if slot is selected
      const isSelected = newSet.has(utcDatetime);
      
      if (isSelected) {
        // Remove from selection
        newSet.delete(utcDatetime);
      } else {
        // Add to selection
        newSet.add(utcDatetime);
      }
      
      return newSet;
    });

    // Mark for syncing to backend
    setPendingSync(true);
  }, []);

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
      className="relative flex flex-col overflow-auto border border-border-primary rounded-lg"
      style={{ userSelect: "none" }}
      ref={containerRef}
    >
      {isLoading && (
        <div className="absolute inset-0 flex items-center justify-center bg-dark-secondary bg-opacity-70 z-20">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-maroon-600"></div>
        </div>
      )}

      {/* Day headers row */}
      <div className="sticky top-0 z-10 flex bg-dark-secondary">
        <div className="w-16 flex-shrink-0 border-r border-b border-border-primary" />
        <div className="flex-1 flex">
          {days.map((day, idx) => (
            <DayHeader
              key={idx}
              date={day}
              width={`${100 / numDays}%`}
              endDate={endDate}
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
          endDate={endDate}
          onDragStart={handleDragStart}
          onDragOver={handleDragOver}
          onDragEnd={handleDragEnd}
          onTapToToggle={handleTapToToggle}
        />
      </div>
    </div>
  );
};

export default WeekCalendar;
