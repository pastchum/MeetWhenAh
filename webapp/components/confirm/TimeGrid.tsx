"use client";

import React from "react";
import TimeSlot from "./TimeSlot";
import { format } from "date-fns";
import { AvailabilityData } from "@/utils/availability_service";

interface TimeGridProps {
  days: Date[];
  timeSlots: number[];
  selectedSlots: Set<string>;
  isDragging: boolean;
  endDate?: Date;
  eventAvailability?: Record<string, AvailabilityData[]>; // All participants' availability data
  readOnly?: boolean;
  onDragStart: (day: string, time: number, isSelected: boolean) => void;
  onDragOver: (day: string, time: number) => void;
  onDragEnd: () => void;
  onTimeSlotClick?: (timeSlot: number) => void;
}

const TimeGrid: React.FC<TimeGridProps> = ({
  days,
  timeSlots,
  selectedSlots,
  isDragging,
  endDate,
  eventAvailability = {},
  readOnly = false,
  onDragStart,
  onDragOver,
  onDragEnd,
  onTimeSlotClick,
}) => {
  // Format date to YYYY-MM-DD for using as a key
  const formatDayKey = (date: Date): string => {
    return format(date, "yyyy-MM-dd");
  };

  // Helper function to convert day and time to ISO datetime
  const getIsoDatetime = (day: string, timeMinutes: number): string => {
    const [year, month, date] = day.split("-").map(Number);
    const hours = Math.floor(timeMinutes / 60);
    const minutes = timeMinutes % 60;

    const dateObj = new Date(year, month - 1, date, hours, minutes);
    return dateObj.toISOString();
  };

  // Helper function to normalize ISO datetime to local timezone for comparison
  const normalizeIsoDatetime = (isoString: string): string => {
    const date = new Date(isoString);
    return date.toISOString();
  };

  // Check if a slot is selected
  const isSlotSelected = (dayKey: string, time: number): boolean => {
    const isoDatetime = getIsoDatetime(dayKey, time);
    const normalizedIsoDatetime = normalizeIsoDatetime(isoDatetime);

    // Check against both the original and normalized versions
    const isSelected =
      selectedSlots.has(isoDatetime) ||
      selectedSlots.has(normalizedIsoDatetime);

    if (isSelected) {
      console.log(`Slot selected: ${dayKey} ${time} -> ${isoDatetime}`);
    }
    return isSelected;
  };

  // Get availability count for a specific time slot
  const getAvailabilityCount = (dayKey: string, time: number): number => {
    const targetDateTime = getIsoDatetime(dayKey, time);
    let count = 0;

    // Check each participant's availability
    Object.values(eventAvailability).forEach((userAvailability) => {
      userAvailability.forEach((block) => {
        const blockStart = new Date(normalizeIsoDatetime(block.start_time));
        const blockEnd = new Date(normalizeIsoDatetime(block.end_time));
        const targetTime = new Date(normalizeIsoDatetime(targetDateTime));

        // Check if target time falls within this availability block
        if (targetTime >= blockStart && targetTime < blockEnd) {
          count++;
        }
      });
    });

    return count;
  };

  // Get total number of participants
  const getTotalParticipants = (): number => {
    return Object.keys(eventAvailability).length;
  };

  // Determine if time is at an hour mark
  const isEvenHour = (time: number): boolean => {
    return time % 60 === 0;
  };

  // Determine if time is at a half hour mark
  const isHalfHour = (time: number): boolean => {
    return time % 60 === 30;
  };

  const totalParticipants = getTotalParticipants();

  return (
    <div className="flex-1 flex">
      {days.map((day, dayIdx) => {
        const dayKey = formatDayKey(day);
        const columnWidth = `${100 / days.length}%`;

        return (
          <div
            key={dayIdx}
            className="border-r border-[#333333]"
            style={{ width: columnWidth }}
          >
            {timeSlots.map((time, timeIdx) => (
              <TimeSlot
                key={timeIdx}
                day={dayKey}
                time={time}
                isSelected={isSlotSelected(dayKey, time)}
                isEvenHour={isEvenHour(time)}
                isHalfHour={isHalfHour(time)}
                isLastRow={timeIdx === timeSlots.length - 1}
                isDragging={isDragging}
                endDate={endDate}
                availabilityCount={getAvailabilityCount(dayKey, time)}
                totalParticipants={totalParticipants}
                readOnly={readOnly}
                onDragStart={onDragStart}
                onDragOver={onDragOver}
                onDragEnd={onDragEnd}
                onClick={() => onTimeSlotClick?.(time)} // Added click handler
              />
            ))}
          </div>
        );
      })}
    </div>
  );
};

export default TimeGrid;
