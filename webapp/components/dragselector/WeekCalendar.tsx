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
  isSlotSelected,
} from "@/utils/datetime-utils";

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

  // Tap selection state
  const [tapStartSlot, setTapStartSlot] = useState<{
    day: string;
    time: number;
  } | null>(null);
  const [tapEndSlot, setTapEndSlot] = useState<{
    day: string;
    time: number;
  } | null>(null);
  const [previewSelection, setPreviewSelection] = useState<Set<string>>(
    new Set()
  );
  const [isInTapMode, setIsInTapMode] = useState(false);
  const [selectionMode, setSelectionMode] = useState<"add" | "remove">("add");

  // Loading state
  const [isLoading, setIsLoading] = useState(false);
  const [syncedWithBackend, setSyncedWithBackend] = useState(false);

  // Generate days array
  const days = Array.from({ length: numDays }, (_, i) => addDays(startDate, i));

  // Time slots (every 30 minutes from 00:00 to 23:30)
  const timeSlots = Array.from({ length: 48 }, (_, i) => i * 30);

  // Container ref for position calculations
  const containerRef = useRef<HTMLDivElement>(null);

  // Helper function to calculate rectangular selection between two points
  const calculateRectangularSelection = useCallback(
    (
      startDay: string,
      startTime: number,
      endDay: string,
      endTime: number
    ): Set<string> => {
      const selection = new Set<string>();

      // Parse dates for comparison
      const startDate = new Date(startDay + "T00:00:00");
      const endDate = new Date(endDay + "T00:00:00");

      // Determine bounds
      const minDate = new Date(
        Math.min(startDate.getTime(), endDate.getTime())
      );
      const maxDate = new Date(
        Math.max(startDate.getTime(), endDate.getTime())
      );
      const minTime = Math.min(startTime, endTime);
      const maxTime = Math.max(startTime, endTime);

      // Get all days within the date range
      const currentDate = new Date(minDate);
      while (currentDate <= maxDate) {
        const dayKey = format(currentDate, "yyyy-MM-dd");

        // Add all time slots within the time range for this day
        for (let time = minTime; time <= maxTime; time += 30) {
          const utcDatetime = getUtcDatetime(dayKey, time);
          selection.add(utcDatetime);
        }

        currentDate.setDate(currentDate.getDate() + 1);
      }

      return selection;
    },
    []
  );

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

      // Save each 30-minute slot individually
      const sortedSlots = Array.from(selectedSlots).sort();

      sortedSlots.forEach((startTime) => {
        // Each slot is exactly 30 minutes
        const startDateTime = new Date(startTime);
        const endDateTime = new Date(startDateTime);
        endDateTime.setMinutes(endDateTime.getMinutes() + 30);

        const data: AvailabilityData = {
          user_uuid: userUuid,
          event_id: eventId,
          start_time: startTime,
          end_time: endDateTime.toISOString(),
        };
        availabilityData.push(data);
      });
      console.log("Syncing availability data:", {
        totalSlots: availabilityData.length,
        slots: availabilityData.map((slot) => ({
          start: slot.start_time,
          end: slot.end_time,
          duration:
            (new Date(slot.end_time).getTime() -
              new Date(slot.start_time).getTime()) /
              (1000 * 60) +
            " minutes",
        })),
      });

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
      console.log(
        "[WeekCalendar] handleSelectWholeDay called with date:",
        date
      );

      // Don't allow selection if date is after end date
      if (endDate && date > endDate) {
        console.log("[WeekCalendar] Date after end date, returning");
        return;
      }

      const dayKey = format(date, "yyyy-MM-dd");
      console.log("[WeekCalendar] Day key:", dayKey);

      // Check if any slots for this day are already selected
      const daySlots = Array.from(selectedSlots).filter((slot) => {
        const { day } = getLocalDayAndTime(slot);
        return day === dayKey;
      });

      const isAnySlotSelected = daySlots.length > 0;
      console.log("[WeekCalendar] Day slots already selected:", daySlots);
      console.log("[WeekCalendar] Is any slot selected:", isAnySlotSelected);

      setSelectedSlots((prev) => {
        console.log("[WeekCalendar] Previous selectedSlots:", Array.from(prev));
        const newSet = new Set(prev);

        if (isAnySlotSelected) {
          // If any slots are selected, deselect the whole day
          console.log("[WeekCalendar] Deselecting whole day");
          timeSlots.forEach((time) => {
            const utcDatetime = getUtcDatetime(dayKey, time);
            newSet.delete(utcDatetime);
          });
        } else {
          // Select all time slots for the day
          console.log("[WeekCalendar] Selecting all time slots for day");
          timeSlots.forEach((time) => {
            const utcDatetime = getUtcDatetime(dayKey, time);
            newSet.add(utcDatetime);
            console.log("[WeekCalendar] Added slot:", {
              dayKey,
              time,
              utcDatetime,
            });
          });
        }

        console.log("[WeekCalendar] New selectedSlots:", Array.from(newSet));
        return newSet;
      });

      // Mark for syncing to backend
      setPendingSync(true);
    },
    [timeSlots, endDate, selectedSlots]
  );

  // Handle tap selection
  const handleTapSelect = useCallback(
    (day: string, time: number) => {
      console.log("[WeekCalendar] Tap select:", {
        day,
        time,
        tapStartSlot,
        tapEndSlot,
      });

      if (!tapStartSlot) {
        // First tap - set start point
        setTapStartSlot({ day, time });
        setIsInTapMode(true);
        setPreviewSelection(new Set([getUtcDatetime(day, time)]));
        console.log("[WeekCalendar] Set tap start:", { day, time });
      } else if (!tapEndSlot) {
        // Second tap - set end point and complete selection
        setTapEndSlot({ day, time });

        // Calculate rectangular selection
        const rectangularSelection = calculateRectangularSelection(
          tapStartSlot.day,
          tapStartSlot.time,
          day,
          time
        );

        console.log("[WeekCalendar] Rectangular selection calculated:", {
          startSlot: tapStartSlot,
          endSlot: { day, time },
          selectionMode,
          selectionSize: rectangularSelection.size,
          selectionDetails: Array.from(rectangularSelection).map((slot) => {
            const { day: slotDay, time: slotTime } = getLocalDayAndTime(slot);
            return { day: slotDay, time: slotTime, utc: slot };
          }),
        });

        // Apply the selection based on mode
        setSelectedSlots((prev) => {
          const newSet = new Set(prev);
          if (selectionMode === "add") {
            rectangularSelection.forEach((slot) => newSet.add(slot));
          } else {
            rectangularSelection.forEach((slot) => newSet.delete(slot));
          }
          return newSet;
        });

        // Clear tap mode
        setTapStartSlot(null);
        setTapEndSlot(null);
        setPreviewSelection(new Set());
        setIsInTapMode(false);

        // Mark for syncing to backend
        setPendingSync(true);
      } else {
        // Already have both points, reset and start over
        setTapStartSlot({ day, time });
        setTapEndSlot(null);
        setPreviewSelection(new Set([getUtcDatetime(day, time)]));
        console.log("[WeekCalendar] Reset and set new tap start:", {
          day,
          time,
        });
      }
    },
    [tapStartSlot, tapEndSlot, calculateRectangularSelection, selectionMode]
  );

  // Handle tap preview (when hovering after first tap)
  const handleTapPreview = useCallback(
    (day: string, time: number) => {
      if (!tapStartSlot || tapEndSlot) return;

      // Calculate and show preview selection
      const rectangularSelection = calculateRectangularSelection(
        tapStartSlot.day,
        tapStartSlot.time,
        day,
        time
      );

      console.log("[WeekCalendar] Preview selection:", {
        from: tapStartSlot,
        to: { day, time },
        previewSize: rectangularSelection.size,
      });

      setPreviewSelection(rectangularSelection);
    },
    [tapStartSlot, tapEndSlot, calculateRectangularSelection]
  );

  // Handle clearing tap mode
  const handleClearTapMode = useCallback(() => {
    setTapStartSlot(null);
    setTapEndSlot(null);
    setPreviewSelection(new Set());
    setIsInTapMode(false);
  }, []);

  // Handle toggling selection mode
  const handleToggleSelectionMode = useCallback(() => {
    setSelectionMode((prev) => (prev === "add" ? "remove" : "add"));
    // Clear tap mode when changing modes
    handleClearTapMode();
  }, [handleClearTapMode]);

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

  // Handle escape key to clear tap mode
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape" && isInTapMode) {
        handleClearTapMode();
      }
    };

    document.addEventListener("keydown", handleKeyDown);
    return () => {
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, [isInTapMode, handleClearTapMode]);

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

      {/* Selection mode toggle button */}
      <div className="flex justify-end p-2 border-b border-border-primary bg-dark-secondary">
        <button
          onClick={handleToggleSelectionMode}
          className={`
            px-3 py-1 rounded text-sm font-medium transition-colors font-ui
            ${
              selectionMode === "add"
                ? "bg-green-600 hover:bg-green-700 text-white"
                : "bg-red-600 hover:bg-red-700 text-white"
            }
          `}
        >
          {selectionMode === "add" ? "➕ Adding" : "➖ Removing"}
        </button>
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
          previewSelection={previewSelection}
          tapStartSlot={tapStartSlot}
          isInTapMode={isInTapMode}
          selectionMode={selectionMode}
          endDate={endDate}
          onTapSelect={handleTapSelect}
          onTapPreview={handleTapPreview}
          onTapToToggle={handleTapToToggle}
          onClearTapMode={handleClearTapMode}
        />
      </div>
    </div>
  );
};

export default WeekCalendar;
