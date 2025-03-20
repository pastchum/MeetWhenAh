'use client';

import React from 'react';
import TimeSlot from './TimeSlot';
import { format } from 'date-fns';

interface TimeGridProps {
  days: Date[];
  timeSlots: number[];
  selectedSlots: Map<string, Set<number>>;
  isDragging: boolean;
  onDragStart: (day: string, time: number, isSelected: boolean) => void;
  onDragOver: (day: string, time: number) => void;
  onDragEnd: () => void;
}

const TimeGrid: React.FC<TimeGridProps> = ({
  days,
  timeSlots,
  selectedSlots,
  isDragging,
  onDragStart,
  onDragOver,
  onDragEnd
}) => {
  // Format date to YYYY-MM-DD for using as a key
  const formatDayKey = (date: Date): string => {
    return format(date, 'yyyy-MM-dd');
  };
  
  // Check if a slot is selected
  const isSlotSelected = (dayKey: string, time: number): boolean => {
    return !!selectedSlots.get(dayKey)?.has(time);
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
    <div className="flex-1 flex">
      {days.map((day, dayIdx) => {
        const dayKey = formatDayKey(day);
        const columnWidth = `${100 / days.length}%`;
        
        return (
          <div 
            key={dayIdx}
            className="border-r border-gray-200"
            style={{ width: columnWidth }}
          >
            {timeSlots.map((time, timeIdx) => (
              <TimeSlot
                key={timeIdx}
                day={dayKey}
                time={time}
                isSelected={isSlotSelected(dayKey, time)}
                isEvenHour={isEvenHour(time)}
                isHalfHour={isHalfHour(time)}
                isLastRow={timeIdx === timeSlots.length - 1}
                isDragging={isDragging}
                onDragStart={onDragStart}
                onDragOver={onDragOver}
                onDragEnd={onDragEnd}
              />
            ))}
          </div>
        );
      })}
    </div>
  );
};

export default TimeGrid; 