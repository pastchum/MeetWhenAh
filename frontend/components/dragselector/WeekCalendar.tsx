'use client';

import React, { useState, useRef, useEffect, useCallback } from 'react';
import DayHeader from './DayHeader';
import TimeColumn from './TimeColumn';
import TimeGrid from './TimeGrid';
import { format, addDays, startOfWeek } from 'date-fns';

interface WeekCalendarProps {
  startDate?: Date;
  numDays?: number;
  onSelectionChange?: (selectedSlots: Map<string, Set<number>>) => void;
}

const WeekCalendar: React.FC<WeekCalendarProps> = ({
  startDate = new Date(),
  numDays = 7,
  onSelectionChange
}) => {
  // Selected slots: Map<dayKey, Set<timeInMinutes>>
  const [selectedSlots, setSelectedSlots] = useState<Map<string, Set<number>>>(
    new Map()
  );
  
  // Drag state
  const [isDragging, setIsDragging] = useState(false);
  const [dragOperation, setDragOperation] = useState<'select' | 'deselect'>('select');
  const [lastSlot, setLastSlot] = useState<{day: string, time: number} | null>(null);
  
  // Generate days array
  const weekStart = startOfWeek(startDate, { weekStartsOn: 1 }); // Week starts Monday
  const days = Array.from({ length: numDays }, (_, i) => addDays(weekStart, i));
  
  // Time slots (every 30 minutes from 00:00 to 23:30)
  const timeSlots = Array.from({ length: 48 }, (_, i) => i * 30);
  
  // Container ref for position calculations
  const containerRef = useRef<HTMLDivElement>(null);
  
  // Handle day header click - select whole day
  const handleSelectWholeDay = useCallback((date: Date) => {
    const dayKey = format(date, 'yyyy-MM-dd');
    
    // Check if any slots for this day are already selected
    const isAnySlotSelected = selectedSlots.has(dayKey) && selectedSlots.get(dayKey)!.size > 0;
    
    setSelectedSlots(prev => {
      const newMap = new Map(prev);
      
      if (isAnySlotSelected) {
        // If any slots are selected, deselect the whole day
        newMap.delete(dayKey);
      } else {
        // Select all time slots for the day
        const allTimes = new Set<number>();
        timeSlots.forEach(time => allTimes.add(time));
        newMap.set(dayKey, allTimes);
      }
      
      return newMap;
    });
  }, [selectedSlots, timeSlots]);
  
  // Handle drag start
  const handleDragStart = useCallback((day: string, time: number, isSelected: boolean) => {
    setIsDragging(true);
    setDragOperation(isSelected ? 'deselect' : 'select');
    setLastSlot({ day, time });
    
    // Update initial selection
    updateSelection(day, time, isSelected ? 'deselect' : 'select');
  }, []);
  
  // Handle drag over time slot
  const handleDragOver = useCallback((day: string, time: number) => {
    if (!isDragging || !lastSlot) return;
    
    // If we moved to a new slot
    if (day !== lastSlot.day || time !== lastSlot.time) {
      updateSelection(day, time, dragOperation);
      setLastSlot({ day, time });
    }
  }, [isDragging, lastSlot, dragOperation]);
  
  // Handle drag end
  const handleDragEnd = useCallback(() => {
    setIsDragging(false);
    setLastSlot(null);
  }, []);
  
  // Update selection based on drag operation
  const updateSelection = (day: string, time: number, operation: 'select' | 'deselect') => {
    setSelectedSlots(prev => {
      const newMap = new Map(prev);
      
      if (operation === 'select') {
        // If selecting, add the time to the day's set
        if (!newMap.has(day)) {
          newMap.set(day, new Set<number>());
        }
        newMap.get(day)?.add(time);
      } else {
        // If deselecting, remove the time from the day's set
        newMap.get(day)?.delete(time);
        // Remove day entirely if no times are selected
        if (newMap.get(day)?.size === 0) {
          newMap.delete(day);
        }
      }
      
      return newMap;
    });
  };
  
  // Notify parent about selection changes
  useEffect(() => {
    onSelectionChange?.(selectedSlots);
  }, [selectedSlots, onSelectionChange]);
  
  // Prevent text selection during dragging
  useEffect(() => {
    const preventDefault = (e: Event) => {
      if (isDragging) {
        e.preventDefault();
      }
    };
    
    document.addEventListener('selectstart', preventDefault);
    return () => {
      document.removeEventListener('selectstart', preventDefault);
    };
  }, [isDragging]);
  
  // Handle drag end when mouse is released anywhere in the document
  useEffect(() => {
    const handleMouseUp = () => {
      if (isDragging) {
        handleDragEnd();
      }
    };
    
    document.addEventListener('mouseup', handleMouseUp);
    document.addEventListener('touchend', handleMouseUp);
    
    return () => {
      document.removeEventListener('mouseup', handleMouseUp);
      document.removeEventListener('touchend', handleMouseUp);
    };
  }, [isDragging, handleDragEnd]);
  
  return (
    <div 
      className="relative flex flex-col overflow-auto border border-gray-200 rounded-lg"
      style={{ userSelect: 'none' }}
      ref={containerRef}
    >
      {/* Day headers row */}
      <div className="sticky top-0 z-10 flex bg-white">
        <div className="w-16 flex-shrink-0 border-r border-b border-gray-200" />
        <div className="flex-1 flex">
          {days.map((day, idx) => (
            <DayHeader 
              key={idx} 
              date={day} 
              width={`${100 / numDays}%`}
              onSelectDay={handleSelectWholeDay}
            />
          ))}
        </div>
      </div>
      
      {/* Calendar body */}
      <div className="flex flex-1">
        {/* Time labels column */}
        <TimeColumn timeSlots={timeSlots} />
        
        {/* Grid of time slots */}
        <TimeGrid
          days={days}
          timeSlots={timeSlots}
          selectedSlots={selectedSlots}
          isDragging={isDragging}
          onDragStart={handleDragStart}
          onDragOver={handleDragOver}
          onDragEnd={handleDragEnd}
        />
      </div>
    </div>
  );
};

export default WeekCalendar; 