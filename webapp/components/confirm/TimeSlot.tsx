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

  // Format time for display (HH:MM)
  const formatTimeLabel = (): string => {
    const hours = Math.floor(time / 60);
    const minutes = time % 60;
    return `${hours.toString().padStart(2, "0")}:${minutes
      .toString()
      .padStart(2, "0")}`;
  };

  // Get background color based on availability count (maroon heat map)
  const getBackgroundColor = (): string => {
    if (isSelected && !readOnly) return "bg-[#8c2e2e] hover:bg-[#722525]";

    if (totalParticipants === 0) return "bg-[#0a0a0a] hover:bg-[#1a1a1a]";

    const percentage = availabilityCount / totalParticipants;
    if (percentage === 1) return "bg-[#722525] hover:bg-[#5a1e1e]";
    if (percentage >= 0.75) return "bg-[#8c2e2e] hover:bg-[#722525]";
    if (percentage >= 0.5) return "bg-[#a83838] hover:bg-[#8c2e2e]";
    if (percentage >= 0.25) return "bg-[#c44545] hover:bg-[#a83838]";
    if (percentage > 0) return "bg-[#d13a3a] hover:bg-[#c44545]";

    return "bg-[#0a0a0a] hover:bg-[#1a1a1a]";
  };

  // Get text color based on selection and availability
  const getTextColor = (): string => {
    if (isSelected && !readOnly) return "text-white";

    if (totalParticipants === 0) return "text-[#a0a0a0]";

    const percentage = availabilityCount / totalParticipants;
    if (percentage >= 0.5) return "text-white";

    return "text-[#e5e5e5]";
  };

  // Get cursor style
  const getCursorStyle = (): string => {
    if (readOnly) return "cursor-default";
    return "cursor-pointer";
  };

  // Handle mouse/touch down
  const handlePointerDown = useCallback(
    (e: React.MouseEvent | React.TouchEvent) => {
      e.preventDefault();
      onDragStart(day, time, isSelected);
    },
    [day, time, isSelected, onDragStart, readOnly]
  );

  // Handle mouse/touch move
  const handlePointerMove = useCallback(() => {
    if (isDragging && !readOnly) {
      onDragOver(day, time);
    }
  }, [day, time, isDragging, onDragOver, readOnly]);

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
      return "border-b-2 border-[#333333]";
    } else if (isEvenHour) {
      // Start of hour (e.g. 1:00) - medium border
      return "border-b border-[#444444]";
    } else {
      // Other time marks - light border
      return "border-b border-[#555555]";
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
