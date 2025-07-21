"use client";

import React, { useState, useRef, useEffect } from "react";
import DayHeader from "./DayHeader";
import TimeColumn from "./TimeColumn";
import TimeGrid from "./TimeGrid";
import { addDays } from "date-fns";
import { fetchEventAvailabilityFromAPI } from "@/routes/availability_routes";
import { AvailabilityData } from "@/utils/availability_service";

interface ConfirmCalendarProps {
  startDate?: Date;
  endDate?: Date;
  numDays?: number;
  eventId?: string;
  onParticipantCountChange?: (count: number) => void;
}

const ConfirmCalendar: React.FC<ConfirmCalendarProps> = ({
  startDate = new Date(),
  endDate = new Date(),
  numDays = 7,
  eventId = "",
  onParticipantCountChange,
}) => {
  // Event availability: Record<tele_id, AvailabilityData[]>
  const [eventAvailability, setEventAvailability] = useState<
    Record<string, AvailabilityData[]>
  >({});

  // Loading state
  const [isLoading, setIsLoading] = useState(false);

  // Generate days array
  const days = Array.from({ length: numDays }, (_, i) => addDays(startDate, i));

  // Time slots (every 30 minutes from 00:00 to 23:30)
  const timeSlots = Array.from({ length: 48 }, (_, i) => i * 30);

  // Container ref for position calculations
  const containerRef = useRef<HTMLDivElement>(null);

  // Fetch event availability data for all participants
  useEffect(() => {
    if (!eventId) return;

    const fetchEventAvailability = async () => {
      setIsLoading(true);
      try {
        const data = await fetchEventAvailabilityFromAPI(eventId);
        if (data) {
          setEventAvailability(data);
          // Notify parent of participant count
          const participantCount = Object.keys(data).length;
          onParticipantCountChange?.(participantCount);
        }
      } catch (error) {
        console.error("Error fetching event availability:", error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchEventAvailability();
  }, [eventId, onParticipantCountChange]);

  // Dummy handlers for TimeGrid (not used in read-only mode)
  const handleDragStart = () => {};
  const handleDragOver = () => {};
  const handleDragEnd = () => {};
  const handleSelectWholeDay = () => {};

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
          selectedSlots={new Set()}
          isDragging={false}
          endDate={endDate}
          eventAvailability={eventAvailability}
          readOnly={true}
          onDragStart={handleDragStart}
          onDragOver={handleDragOver}
          onDragEnd={handleDragEnd}
        />
      </div>
    </div>
  );
};

export default ConfirmCalendar;
