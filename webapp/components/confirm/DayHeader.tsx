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
      className={`p-2 border-r border-b border-[#333333] font-medium transition-colors duration-150 ${
        isDisabled
          ? "bg-[#1a1a1a] text-[#666666] cursor-not-allowed"
          : "bg-[#0a0a0a] text-[#e5e5e5] cursor-pointer hover:bg-[#1a1a1a]"
      }`}
      style={{ width }}
      onClick={handleClick}
    >
      <div className="text-center">
        <div className="text-sm text-[#e5e5e5]">{format(date, "EEE")}</div>
        <div className="text-xs text-[#a0a0a0]">{format(date, "MMM d")}</div>
      </div>
    </div>
  );
};

export default DayHeader;
