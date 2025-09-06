"use client";

import React from "react";

interface TimeColumnProps {
  timeSlots: number[];
}

const TimeColumn: React.FC<TimeColumnProps> = ({ timeSlots }) => {
  // Format minutes as HH:MM
  const formatTime = (minutes: number): string => {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return `${hours.toString().padStart(2, "0")}:${mins
      .toString()
      .padStart(2, "0")}`;
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
    <div className="w-16 flex-shrink-0 border-r border-border-primary bg-dark-secondary">
      {timeSlots.map((minutes, idx) => {
        const isHour = isEvenHour(minutes);
        const isHalf = isHalfHour(minutes);
        const isLastRow = idx === timeSlots.length - 1;

        return (
          <div
            key={idx}
            className={`
              h-8 px-2 flex items-center justify-end text-xs
              ${isLastRow ? "border-b-0" : "border-b-2 border-border-primary"}
              ${
                isHour
                  ? "font-semibold text-text-primary"
                  : "font-medium text-text-secondary"
              }
            `}
          >
            {formatTime(minutes)}
          </div>
        );
      })}
    </div>
  );
};

export default TimeColumn;
