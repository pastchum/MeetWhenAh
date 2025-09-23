"use client";

import React, { useCallback } from "react";
import { format } from "date-fns";

interface DayHeaderProps {
  date: Date;
  width: string;
  endDate?: Date;
  onSelectDay: (date: Date) => void;
}

const DayHeader: React.FC<DayHeaderProps> = ({
  date,
  width,
  endDate,
  onSelectDay,
}) => {
  const isDisabled = endDate ? date > endDate : false;

  const handleClick = useCallback(() => {
    console.log('[DayHeader] Click detected:', { date, isDisabled });
    if (!isDisabled) {
      console.log('[DayHeader] Calling onSelectDay with date:', date);
      onSelectDay(date);
    } else {
      console.log('[DayHeader] Day is disabled, not calling onSelectDay');
    }
  }, [date, onSelectDay, isDisabled]);

  return (
    <div
      className={`p-2 border-r border-b border-border-primary font-medium transition-colors duration-150 font-ui ${
        isDisabled
          ? "bg-dark-tertiary text-text-disabled cursor-not-allowed"
          : "bg-dark-secondary text-text-primary cursor-pointer hover:bg-selection-hover"
      }`}
      style={{ width }}
      onClick={handleClick}
    >
      <div className="text-center">
        <div className="text-sm text-text-primary font-body">{format(date, "EEE")}</div>
        <div className="text-xs text-text-secondary font-caption">{format(date, "MMM d")}</div>
      </div>
    </div>
  );
};

export default DayHeader;
