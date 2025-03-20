'use client';

import React, { useRef, useCallback } from 'react';

interface TimeSlotProps {
  day: string;
  time: number;
  isSelected: boolean;
  isEvenHour: boolean;
  isDragging: boolean;
  onDragStart: (day: string, time: number, isSelected: boolean) => void;
  onDragOver: (day: string, time: number) => void;
  onDragEnd: () => void;
}

const TimeSlot: React.FC<TimeSlotProps> = ({
  day,
  time,
  isSelected,
  isEvenHour,
  isDragging,
  onDragStart,
  onDragOver,
  onDragEnd
}) => {
  const slotRef = useRef<HTMLDivElement>(null);
  
  // Format time for display (HH:MM)
  const formatTimeLabel = (): string => {
    const hours = Math.floor(time / 60);
    const minutes = time % 60;
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}`;
  };
  
  // Handle mouse/touch down
  const handlePointerDown = useCallback((e: React.MouseEvent | React.TouchEvent) => {
    e.preventDefault();
    onDragStart(day, time, isSelected);
  }, [day, time, isSelected, onDragStart]);
  
  // Handle mouse/touch move
  const handlePointerMove = useCallback(() => {
    if (isDragging) {
      onDragOver(day, time);
    }
  }, [day, time, isDragging, onDragOver]);
  
  // Handle mouse/touch up
  const handlePointerUp = useCallback(() => {
    if (isDragging) {
      onDragEnd();
    }
  }, [isDragging, onDragEnd]);
  
  return (
    <div
      ref={slotRef}
      className={`
        h-8 border-b ${isEvenHour ? 'border-gray-200' : 'border-gray-100'}
        ${isSelected ? 'bg-blue-500 hover:bg-blue-600' : 'bg-white hover:bg-gray-50'}
        transition-colors duration-100 ease-in-out
        ${isSelected ? 'text-white' : 'text-gray-700'}
      `}
      onMouseDown={handlePointerDown}
      onTouchStart={handlePointerDown}
      onMouseMove={handlePointerMove}
      onTouchMove={handlePointerMove}
      onMouseUp={handlePointerUp}
      onTouchEnd={handlePointerUp}
      data-day={day}
      data-time={time}
    >
      <div className="h-full w-full flex items-center justify-center text-xs">
        {/* Optionally show the time label for debugging */}
        {/* {formatTimeLabel()} */}
      </div>
    </div>
  );
};

export default TimeSlot; 