'use client';

import React from 'react';

interface TimeColumnProps {
  timeSlots: number[];
}

const TimeColumn: React.FC<TimeColumnProps> = ({ timeSlots }) => {
  // Format minutes as HH:MM
  const formatTime = (minutes: number): string => {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return `${hours.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}`;
  };

  return (
    <div className="w-16 flex-shrink-0 border-r border-gray-200">
      {timeSlots.map((minutes, idx) => (
        <div 
          key={idx} 
          className={`
            h-8 px-2 flex items-center justify-end text-xs text-gray-500
            ${idx % 2 === 0 ? 'border-b border-gray-200 font-medium' : 'border-b border-gray-100'}
          `}
        >
          {idx % 2 === 0 && formatTime(minutes)}
        </div>
      ))}
    </div>
  );
};

export default TimeColumn; 