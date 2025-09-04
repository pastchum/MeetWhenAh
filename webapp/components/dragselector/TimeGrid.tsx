"use client";

import React from "react";
import TimeSlot from "./TimeSlot";
import { format } from "date-fns";
import { isSlotSelected } from "@/utils/datetime-utils";

interface TimeGridProps {
  days: Date[];
  timeSlots: number[];
  selectedSlots: Set<string>;
  isDragging: boolean;
  endDate?: Date;
  onDragStart: (day: string, time: number, isSelected: boolean) => void;
  onDragOver: (day: string, time: number) => void;
  onDragEnd: () => void;
  onTapToToggle?: (day: string, time: number) => void;
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
  onTapToToggle,
}) => {
  // Format date to YYYY-MM-DD for using as a key
  const formatDayKey = (date: Date): string => {
    return format(date, "yyyy-MM-dd");
  };

  // Check if a slot is selected using unified utility function
  const checkSlotSelected = (dayKey: string, time: number): boolean => {
    const isSelected = isSlotSelected(dayKey, time, selectedSlots);

    // Only log for first few slots or when selected
    // if (time < 180 || isSelected) {
    //   console.log('[TimeGrid] isSlotSelected check:', {
    //     dayKey,
    //     time,
    //     isSelected,
    //     selectedSlotsSize: selectedSlots.size
    //   });
    // }

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
            className="border-r border-border-primary"
            style={{ width: columnWidth }}
          >
            {timeSlots.map((time, timeIdx) => {
              const slotIsSelected = checkSlotSelected(dayKey, time);
              
              // Only log for first few slots or when selected
              // if (time < 180 || slotIsSelected) {
              //   console.log('[TimeGrid] Rendering TimeSlot:', {
              //     dayKey,
              //     time,
              //     slotIsSelected,
              //     timeIdx
              //   });
              // }
              
              return (
                <TimeSlot
                  key={timeIdx}
                  day={dayKey}
                  time={time}
                  isSelected={slotIsSelected}
                  isEvenHour={isEvenHour(time)}
                  isHalfHour={isHalfHour(time)}
                  isLastRow={timeIdx === timeSlots.length - 1}
                  isDragging={isDragging}
                  endDate={endDate}
                  onDragStart={onDragStart}
                  onDragOver={onDragOver}
                  onDragEnd={onDragEnd}
                  onTapToToggle={onTapToToggle}
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
