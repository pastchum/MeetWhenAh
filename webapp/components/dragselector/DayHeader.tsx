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
    if (!isDisabled) {
      onSelectDay(date);
    }
  }, [date, onSelectDay, isDisabled]);

  return (
    <div
      className={`p-2 border-r border-b border-gray-200 font-medium transition-colors duration-150 ${
        isDisabled
          ? "bg-gray-100 text-gray-400 cursor-not-allowed"
          : "bg-gray-50 text-gray-700 cursor-pointer hover:bg-blue-50"
      }`}
      style={{ width }}
      onClick={handleClick}
    >
      <div className="text-center">
        <div className="text-sm text-gray-700">{format(date, "EEE")}</div>
        <div className="text-xs text-gray-500">{format(date, "MMM d")}</div>
      </div>
    </div>
  );
};

export default DayHeader;
