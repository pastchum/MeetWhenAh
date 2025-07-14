"use client";

import React, { useRef, useCallback } from "react";

interface TimeSlotProps {
  day: string;
  time: number;
  isSelected: boolean;
  isEvenHour: boolean;
  isHalfHour: boolean;
  isLastRow: boolean;
  isDragging: boolean;
  endDate?: Date;
  onDragStart: (day: string, time: number, isSelected: boolean) => void;
  onDragOver: (day: string, time: number) => void;
  onDragEnd: () => void;
}

const TimeSlot: React.FC<TimeSlotProps> = ({
  day,
  time,
  isSelected,
  isEvenHour,
  isHalfHour,
  isLastRow,
  isDragging,
  endDate,
  onDragStart,
  onDragOver,
  onDragEnd,
}) => {
  const slotRef = useRef<HTMLDivElement>(null);

  // Check if this slot is disabled (date is after end date)
  const isDisabled = endDate ? new Date(day) > endDate : false;

  // Format time for display (HH:MM)
  const formatTimeLabel = (): string => {
    const hours = Math.floor(time / 60);
    const minutes = time % 60;
    return `${hours.toString().padStart(2, "0")}:${minutes
      .toString()
      .padStart(2, "0")}`;
  };

  // Handle mouse/touch down
  const handlePointerDown = useCallback(
    (e: React.MouseEvent | React.TouchEvent) => {
      if (isDisabled) return;
      e.preventDefault();
      onDragStart(day, time, isSelected);
    },
    [day, time, isSelected, onDragStart, isDisabled]
  );

  // Handle mouse/touch move
  const handlePointerMove = useCallback(() => {
    if (isDragging && !isDisabled) {
      onDragOver(day, time);
    }
  }, [day, time, isDragging, onDragOver, isDisabled]);

  // Handle mouse/touch up
  const handlePointerUp = useCallback(() => {
    if (isDragging) {
      onDragEnd();
    }
  }, [isDragging, onDragEnd]);

  // Determine border style based on time - SWAPPED HIERARCHY
  const getBorderStyle = () => {
    // Make the last row's bottom border transparent
    if (isLastRow) {
      return "border-b-0";
    }

    if (isHalfHour) {
      // Half hour mark (e.g. 1:30) - darker border
      return "border-b-2 border-gray-800";
    } else if (isEvenHour) {
      // Start of hour (e.g. 1:00) - medium border
      return "border-b border-gray-400";
    } else {
      // Other time marks - light border
      return "border-b border-gray-200";
    }
  };

  return (
    <div
      ref={slotRef}
      className={`
        h-8 ${getBorderStyle()}
        ${
          isDisabled
            ? "bg-gray-100 cursor-not-allowed"
            : isSelected
            ? "bg-blue-500 hover:bg-blue-600"
            : "bg-white hover:bg-gray-50"
        }
        transition-colors duration-100 ease-in-out
        ${
          isDisabled
            ? "text-gray-400"
            : isSelected
            ? "text-white"
            : "text-gray-700"
        }
      `}
      onMouseDown={handlePointerDown}
      onTouchStart={handlePointerDown}
      onMouseMove={handlePointerMove}
      onTouchMove={handlePointerMove}
      onMouseUp={handlePointerUp}
      onTouchEnd={handlePointerUp}
      data-day={day}
      data-time={time}
    >
      <div className="h-full w-full flex items-center justify-center text-xs">
        {/* Optionally show the time label for debugging */}
        {/* {formatTimeLabel()} */}
      </div>
    </div>
  );
};

export default TimeSlot;
