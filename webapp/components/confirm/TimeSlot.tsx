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
  availabilityCount?: number; // Number of participants available in this slot
  totalParticipants?: number; // Total number of participants in the event
  readOnly?: boolean;
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
  availabilityCount = 0,
  totalParticipants = 0,
  readOnly = false,
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

  // Get background color based on availability count (blue heat map)
  const getBackgroundColor = (): string => {
    if (isDisabled) return "bg-gray-100";
    if (isSelected && !readOnly) return "bg-blue-500 hover:bg-blue-600";

    if (totalParticipants === 0) return "bg-gray-50 hover:bg-gray-100";

    const percentage = availabilityCount / totalParticipants;
    if (percentage === 1) return "bg-blue-600 hover:bg-blue-700";
    if (percentage >= 0.75) return "bg-blue-400 hover:bg-blue-500";
    if (percentage >= 0.5) return "bg-blue-200 hover:bg-blue-300";
    if (percentage >= 0.25) return "bg-blue-100 hover:bg-blue-200";
    if (percentage > 0) return "bg-blue-50 hover:bg-blue-100";

    return "bg-gray-50 hover:bg-gray-100";
  };

  // Get text color based on selection and availability
  const getTextColor = (): string => {
    if (isDisabled) return "text-gray-400";
    if (isSelected && !readOnly) return "text-white";

    if (totalParticipants === 0) return "text-gray-500";

    const percentage = availabilityCount / totalParticipants;
    if (percentage >= 0.5) return "text-white";

    return "text-gray-700";
  };

  // Get cursor style
  const getCursorStyle = (): string => {
    if (isDisabled) return "cursor-not-allowed";
    if (readOnly) return "cursor-default";
    return "cursor-pointer";
  };

  // Handle mouse/touch down
  const handlePointerDown = useCallback(
    (e: React.MouseEvent | React.TouchEvent) => {
      if (isDisabled || readOnly) return;
      e.preventDefault();
      onDragStart(day, time, isSelected);
    },
    [day, time, isSelected, onDragStart, isDisabled, readOnly]
  );

  // Handle mouse/touch move
  const handlePointerMove = useCallback(() => {
    if (isDragging && !isDisabled && !readOnly) {
      onDragOver(day, time);
    }
  }, [day, time, isDragging, onDragOver, isDisabled, readOnly]);

  // Handle mouse/touch up
  const handlePointerUp = useCallback(() => {
    if (isDragging && !readOnly) {
      onDragEnd();
    }
  }, [isDragging, onDragEnd, readOnly]);

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
        ${getBackgroundColor()}
        transition-colors duration-100 ease-in-out
        ${getTextColor()}
        ${getCursorStyle()}
      `}
      onMouseDown={handlePointerDown}
      onTouchStart={handlePointerDown}
      onMouseMove={handlePointerMove}
      onTouchMove={handlePointerMove}
      onMouseUp={handlePointerUp}
      onTouchEnd={handlePointerUp}
      data-day={day}
      data-time={time}
      title={`${availabilityCount}/${totalParticipants} participants available`}
    >
      <div className="h-full w-full flex items-center justify-center text-xs font-medium">
        {availabilityCount > 0 && totalParticipants > 0 && (
          <span>{availabilityCount}</span>
        )}
      </div>
    </div>
  );
};

export default TimeSlot;
