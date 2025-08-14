"use client";

import React, { useRef, useCallback } from "react";
import { Chip } from "@nextui-org/react";

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
  onTapToToggle?: (day: string, time: number) => void;
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
  onTapToToggle,
}) => {
  // Log the props received (only for first few slots or when selected)
  // if (time < 180 || isSelected) {
  //   console.log('[TimeSlot] Props received:', {
  //     day,
  //     time,
  //     isSelected,
  //     isDragging,
  //     isDisabled: endDate ? new Date(day) > endDate : false
  //   });
  // }
  const slotRef = useRef<HTMLDivElement>(null);

  // Check if this slot is disabled (date is after end date)
  // Check if this slot is disabled (date is after end date)
  const isDisabled = endDate
    ? (() => {
        // Parse day string (YYYY-MM-DD) as a date in local timezone
        const dayDate = new Date(day + "T00:00:00");
        // Normalize endDate to start of day for proper comparison
        const endDateStartOfDay = new Date(
          endDate.getFullYear(),
          endDate.getMonth(),
          endDate.getDate()
        );
        return dayDate > endDateStartOfDay;
      })()
    : false;
  // Handle mouse/touch down for drag start
  const handlePointerDown = useCallback(
    (e: React.MouseEvent | React.TouchEvent) => {
      if (isDisabled) return;
      e.preventDefault();
      // console.log('[TimeSlot] Pointer down:', { day, time, isSelected, type: e.type });
      onDragStart(day, time, isSelected);
    },
    [day, time, isSelected, onDragStart, isDisabled]
  );

  // Handle mouse/touch move for drag
  const handlePointerMove = useCallback(() => {
    if (isDragging && !isDisabled) {
      // console.log('[TimeSlot] Pointer move:', { day, time, isDragging });
      onDragOver(day, time);
    }
  }, [day, time, isDragging, onDragOver, isDisabled]);

  // Handle mouse/touch up for drag end
  const handlePointerUp = useCallback(() => {
    if (isDragging) {
      onDragEnd();
    }
  }, [isDragging, onDragEnd]);

  // Handle tap to toggle selection (when not dragging)
  const handleClick = useCallback(
    (e: React.MouseEvent | React.TouchEvent) => {
      if (isDisabled || isDragging) return;
      e.preventDefault();
      e.stopPropagation();
      onTapToToggle?.(day, time);
    },
    [day, time, isDisabled, isDragging, onTapToToggle]
  );

  // Determine border style based on time
  const getBorderStyle = () => {
    if (isLastRow) {
      return "border-b-0";
    }

    if (isHalfHour) {
      return "border-b-2 border-border-primary";
    } else if (isEvenHour) {
      return "border-b border-border-secondary";
    } else {
      return "border-b border-border-primary";
    }
  };

  return (
    <div
      ref={slotRef}
      className={`h-8 ${getBorderStyle()}`}
      onMouseDown={handlePointerDown}
      onTouchStart={handlePointerDown}
      onMouseMove={handlePointerMove}
      onTouchMove={handlePointerMove}
      onMouseUp={handlePointerUp}
      onTouchEnd={handlePointerUp}
      onClick={handleClick}
      data-day={day}
      data-time={time}
    >
      <Chip
        variant={isSelected ? "solid" : "bordered"}
        color={isSelected ? "primary" : "default"}
        size="sm"
        className={`
          w-full h-full rounded-none
          ${isDragging && isSelected ? "scale-95" : ""}
        `}
        classNames={{
          base: isDisabled
            ? "bg-dark-tertiary cursor-not-allowed border-0"
            : "border-0",
          content: "p-0",
        }}
        isDisabled={isDisabled}
      >
        {/* Empty content - just for visual styling */}
      </Chip>
    </div>
  );
};

export default TimeSlot;
