"use client";

import React from "react";
import TimeSlot from "./TimeSlot";
import { format } from "date-fns";
import { isSlotSelected } from "@/utils/datetime-utils";

interface TimeGridProps {
  days: Date[];
  timeSlots: number[];
  selectedSlots: Set<string>;
  previewSelection: Set<string>;
  tapStartSlot: { day: string; time: number } | null;
  isInTapMode: boolean;
  selectionMode: "add" | "remove";
  endDate?: Date;
  onTapSelect: (day: string, time: number) => void;
  onTapPreview: (day: string, time: number) => void;
  onTapToToggle?: (day: string, time: number) => void;
  onClearTapMode: () => void;
}

const TimeGrid: React.FC<TimeGridProps> = ({
  days,
  timeSlots,
  selectedSlots,
  previewSelection,
  tapStartSlot,
  isInTapMode,
  selectionMode,
  endDate,
  onTapSelect,
  onTapPreview,
  onTapToToggle,
  onClearTapMode,
}) => {
  // Format date to YYYY-MM-DD for using as a key
  const formatDayKey = (date: Date): string => {
    return format(date, "yyyy-MM-dd");
  };

  // Check if a slot is selected using unified utility function
  const checkSlotSelected = (dayKey: string, time: number): boolean => {
    return isSlotSelected(dayKey, time, selectedSlots);
  };

  // Check if a slot is in the preview selection
  const checkSlotInPreview = (dayKey: string, time: number): boolean => {
    return isSlotSelected(dayKey, time, previewSelection);
  };

  // Check if a slot is the tap start slot
  const checkIsTapStart = (dayKey: string, time: number): boolean => {
    return (
      tapStartSlot !== null &&
      tapStartSlot.day === dayKey &&
      tapStartSlot.time === time
    );
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
            className="border-r border-border-primary"
            style={{ width: columnWidth }}
          >
            {timeSlots.map((time, timeIdx) => {
              const slotIsSelected = checkSlotSelected(dayKey, time);
              const slotInPreview = checkSlotInPreview(dayKey, time);
              const isTapStart = checkIsTapStart(dayKey, time);

              return (
                <TimeSlot
                  key={timeIdx}
                  day={dayKey}
                  time={time}
                  isSelected={slotIsSelected}
                  isInPreview={slotInPreview}
                  isTapStart={isTapStart}
                  isInTapMode={isInTapMode}
                  selectionMode={selectionMode}
                  isEvenHour={isEvenHour(time)}
                  isHalfHour={isHalfHour(time)}
                  isLastRow={timeIdx === timeSlots.length - 1}
                  endDate={endDate}
                  onTapSelect={onTapSelect}
                  onTapPreview={onTapPreview}
                  onTapToToggle={onTapToToggle}
                  onClearTapMode={onClearTapMode}
                />
              );
            })}
          </div>
        );
      })}
    </div>
  );
};

export default TimeGrid;
