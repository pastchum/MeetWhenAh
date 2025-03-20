'use client'
import React, { useState } from 'react';
import WeekCalendar from '../../components/dragselector/WeekCalendar';
import { addDays } from 'date-fns';

export default function DragSelectorPage() {
  const [startDate, setStartDate] = useState<Date>(new Date());
  const [numDays, setNumDays] = useState<number>(7);
  const [selectionData, setSelectionData] = useState<Map<string, Set<number>>>(new Map());
  
  // Handle previous/next week
  const navigatePreviousWeek = () => {
    setStartDate(prev => addDays(prev, -numDays));
  };
  
  const navigateNextWeek = () => {
    setStartDate(prev => addDays(prev, numDays));
  };
  
  // Format selection data for display/save
  const formatSelectionSummary = () => {
    const summary: string[] = [];
    
    selectionData.forEach((times, day) => {
      const formattedTimes = Array.from(times)
        .sort((a, b) => a - b)
        .map(minutes => {
          const hours = Math.floor(minutes / 60);
          const mins = minutes % 60;
          return `${hours.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}`;
        })
        .join(', ');
      
      summary.push(`${day}: ${formattedTimes}`);
    });
    
    return summary.join('\n');
  };
  
  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Weekly Availability Selector</h1>
      
      <div className="mb-4 flex justify-between items-center">
        <button
          onClick={navigatePreviousWeek}
          className="px-4 py-2 bg-gray-200 hover:bg-gray-300 rounded"
        >
          Previous Week
        </button>
        
        <button
          onClick={navigateNextWeek}
          className="px-4 py-2 bg-gray-200 hover:bg-gray-300 rounded"
        >
          Next Week
        </button>
      </div>
      
      <div className="bg-white rounded-lg shadow-md">
        <WeekCalendar
          startDate={startDate}
          numDays={numDays}
          onSelectionChange={setSelectionData}
        />
      </div>
      
      <div className="mt-4">
        <h2 className="text-xl font-semibold mb-2">Selected Times</h2>
        <pre className="bg-gray-100 p-4 rounded whitespace-pre-wrap">
          {selectionData.size > 0 ? formatSelectionSummary() : 'No times selected.'}
        </pre>
      </div>
    </div>
  );
}
