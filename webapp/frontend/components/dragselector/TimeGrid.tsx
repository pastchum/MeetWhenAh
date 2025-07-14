"use client";

import React from "react";
import TimeSlot from "./TimeSlot";
import { format } from "date-fns";

interface TimeGridProps {
  days: Date[];
  timeSlots: number[];
  selectedSlots: Set<string>;
  isDragging: boolean;
  endDate?: Date;
  onDragStart: (day: string, time: number, isSelected: boolean) => void;
  onDragOver: (day: string, time: number) => void;
  onDragEnd: () => void;
}

const TimeGrid: React.FC<TimeGridProps> = ({
  days,
  timeSlots,
  selectedSlots,
  isDragging,
  endDate,
  onDragStart,
  onDragOver,
  onDragEnd,
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
    const year = date.getFullYear();
    const month = date.getMonth() + 1;
    const day = date.getDate();
    const hours = date.getHours();
    const minutes = date.getMinutes();

    // Recreate the date in local timezone to ensure consistent timezone handling
    const localDate = new Date(year, month - 1, day, hours, minutes);
    return localDate.toISOString();
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

  // Determine if time is at an hour mark
  const isEvenHour = (time: number): boolean => {
    return time % 60 === 0;
  };

  // Determine if time is at a half hour mark
  const isHalfHour = (time: number): boolean => {
    return time % 60 === 30;
  };

  return (
    <div className="flex-1 flex">
      {days.map((day, dayIdx) => {
        const dayKey = formatDayKey(day);
        const columnWidth = `${100 / days.length}%`;

        return (
          <div
            key={dayIdx}
            className="border-r border-gray-200"
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
                onDragStart={onDragStart}
                onDragOver={onDragOver}
                onDragEnd={onDragEnd}
              />
            ))}
          </div>
        );
      })}
    </div>
  );
};

export default TimeGrid;
