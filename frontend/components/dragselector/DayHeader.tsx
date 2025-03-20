'use client';

import React, { useCallback } from 'react';
import { format } from 'date-fns';

interface DayHeaderProps {
  date: Date;
  width: string;
  onSelectDay: (date: Date) => void;
}

const DayHeader: React.FC<DayHeaderProps> = ({ date, width, onSelectDay }) => {
  const handleClick = useCallback(() => {
    onSelectDay(date);
  }, [date, onSelectDay]);

  return (
    <div 
      className="p-2 border-r border-b border-gray-200 bg-gray-50 font-medium cursor-pointer hover:bg-blue-50 transition-colors duration-150"
      style={{ width }}
      onClick={handleClick}
    >
      <div className="text-center">
        <div className="text-sm text-gray-700">{format(date, 'EEE')}</div>
        <div className="text-xs text-gray-500">{format(date, 'MMM d')}</div>
      </div>
    </div>
  );
};

export default DayHeader; 