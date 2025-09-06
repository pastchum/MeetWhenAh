"use client";

import React, { useRef, useCallback } from "react";
import { Chip } from "@nextui-org/react";

interface TimeSlotProps {
  day: string;
  time: number;
  isSelected: boolean;
  isInPreview: boolean;
  isTapStart: boolean;
  isInTapMode: boolean;
  selectionMode: "add" | "remove";
  isEvenHour: boolean;
  isHalfHour: boolean;
  isLastRow: boolean;
  endDate?: Date;
  onTapSelect: (day: string, time: number) => void;
  onTapPreview: (day: string, time: number) => void;
  onTapToToggle?: (day: string, time: number) => void;
  onClearTapMode: () => void;
}

const TimeSlot: React.FC<TimeSlotProps> = ({
  day,
  time,
  isSelected,
  isInPreview,
  isTapStart,
  isInTapMode,
  selectionMode,
  isEvenHour,
  isHalfHour,
  isLastRow,
  endDate,
  onTapSelect,
  onTapPreview,
  onTapToToggle,
  onClearTapMode,
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
  // Handle tap selection
  const handleTapSelect = useCallback(
    (e: React.MouseEvent | React.TouchEvent) => {
      if (isDisabled) return;
      e.preventDefault();
      e.stopPropagation();

      // Check if we should start tap mode or toggle individual slot
      // If no modifier keys, start/continue tap mode
      // If with modifier (like Ctrl/Cmd), toggle individual slot
      if (e.ctrlKey || e.metaKey) {
        // Toggle individual slot
        onTapToToggle?.(day, time);
      } else {
        // Use tap select logic
        onTapSelect(day, time);
      }
    },
    [day, time, isDisabled, onTapSelect, onTapToToggle]
  );

  // Handle hover for preview when in tap mode
  const handleMouseEnter = useCallback(() => {
    if (isInTapMode && !isDisabled) {
      onTapPreview(day, time);
    }
  }, [day, time, isInTapMode, isDisabled, onTapPreview]);

  // Handle right click to clear tap mode
  const handleContextMenu = useCallback(
    (e: React.MouseEvent) => {
      e.preventDefault();
      if (isInTapMode) {
        onClearTapMode();
      }
    },
    [isInTapMode, onClearTapMode]
  );

  // Determine border style based on time
  const getBorderStyle = () => {
    if (isLastRow) {
      return "border-b-0";
    }

    // Give equal visual weight to all 30-minute intervals
    return "border-b-2 border-border-primary";
  };

  // Determine visual state
  const getChipVariant = () => {
    if (isSelected) return "solid";
    if (isInPreview) return "flat";
    return "bordered";
  };

  const getChipColor = () => {
    if (isSelected) return "primary";
    if (isTapStart) {
      return selectionMode === "add" ? "success" : "danger";
    }
    if (isInPreview) {
      return selectionMode === "add" ? "success" : "danger";
    }
    return "default";
  };

  const getChipClassName = () => {
    let className = "w-full h-full rounded-none transition-all duration-200";

    if (isTapStart) {
      const ringColor =
        selectionMode === "add" ? "ring-green-400" : "ring-red-400";
      className += ` ring-2 ${ringColor} ring-offset-1`;
    }
    if (isInPreview && !isSelected) {
      className += " opacity-70";
    }
    if (isInTapMode && !isDisabled) {
      className += " cursor-crosshair";
    }

    return className;
  };

  return (
    <div
      ref={slotRef}
      className={`h-8 ${getBorderStyle()}`}
      onClick={handleTapSelect}
      onMouseEnter={handleMouseEnter}
      onContextMenu={handleContextMenu}
      data-day={day}
      data-time={time}
    >
      <Chip
        variant={getChipVariant()}
        color={getChipColor()}
        size="sm"
        className={getChipClassName()}
        classNames={{
          base: isDisabled
            ? "bg-dark-tertiary cursor-not-allowed border-0"
            : "border-0",
          content: "p-0",
        }}
        isDisabled={isDisabled}
      >
        {/* Show indicator for tap start */}
        {isTapStart && (
          <div
            className={`w-2 h-2 rounded-full ${
              selectionMode === "add" ? "bg-green-500" : "bg-red-500"
            }`}
          />
        )}
      </Chip>
    </div>
  );
};

export default TimeSlot;
