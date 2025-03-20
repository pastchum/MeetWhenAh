'use client';

import React from 'react';
import { format } from 'date-fns';

interface DayHeaderProps {
  date: Date;
  width: string;
}

const DayHeader: React.FC<DayHeaderProps> = ({ date, width }) => {
  return (
    <div 
      className="p-2 border-r border-b border-gray-200 bg-gray-50 font-medium"
      style={{ width }}
    >
      <div className="text-center">
        <div className="text-sm text-gray-700">{format(date, 'EEE')}</div>
        <div className="text-xs text-gray-500">{format(date, 'MMM d')}</div>
      </div>
    </div>
  );
};

export default DayHeader; 