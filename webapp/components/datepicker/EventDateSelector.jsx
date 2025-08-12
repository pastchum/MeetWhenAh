import { Button } from "@nextui-org/react";
import NextButton from "@/components/datepicker/NextButton";
import PreviousButton from "@/components/datepicker/PreviousButton";
import { useState } from "react";

export default function EventDateSelector({
  prevComponent,
  nextComponent,
  initialData = null
}) {
  const [newData, setNewData] = useState(() => {
    if (initialData?.start && initialData?.end) {
      try {
        // If initialData has string dates, convert them
        if (typeof initialData.start === 'string') {
          const startDate = new Date(initialData.start);
          const endDate = new Date(initialData.end);
          return {
            start: startDate,
            end: endDate
          };
        }
      } catch (error) {
        console.warn('Error parsing initial dates:', error);
      }
    }
    
    // Start with null as default
    return {
      start: null,
      end: null,
    };
  });

  const [currentMonth, setCurrentMonth] = useState(new Date());
  const [selectionMode, setSelectionMode] = useState('start'); // 'start' or 'end'

  const handleClear = () => {
    setNewData({
      start: null,
      end: null,
    });
    setSelectionMode('start');
  };

  const handleDateSelect = (date) => {
    if (selectionMode === 'start') {
      setNewData({
        start: date,
        end: newData.end
      });
      setSelectionMode('end');
    } else {
      // If end date is before start date, swap them
      if (date < newData.start) {
        setNewData({
          start: date,
          end: newData.start
        });
      } else {
        setNewData({
          start: newData.start,
          end: date
        });
      }
      setSelectionMode('start');
    }
  };

  const handleInputChange = (type, value) => {
    try {
      const date = new Date(value);
      if (!isNaN(date.getTime())) {
        if (type === 'start') {
          setNewData({
            start: date,
            end: newData.end
          });
        } else {
          setNewData({
            start: newData.start,
            end: date
          });
        }
      }
    } catch (error) {
      console.warn('Error parsing date:', error);
    }
  };

  const goToPreviousMonth = () => {
    setCurrentMonth(prev => {
      const newMonth = new Date(prev);
      newMonth.setMonth(prev.getMonth() - 1);
      return newMonth;
    });
  };

  const goToNextMonth = () => {
    setCurrentMonth(prev => {
      const newMonth = new Date(prev);
      newMonth.setMonth(prev.getMonth() + 1);
      return newMonth;
    });
  };

  const getDaysInMonth = (date) => {
    const year = date.getFullYear();
    const month = date.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const daysInMonth = lastDay.getDate();
    const startingDayOfWeek = firstDay.getDay();
    
    return { daysInMonth, startingDayOfWeek };
  };

  const isDateInRange = (date) => {
    if (!newData.start || !newData.end) return false;
    return date >= newData.start && date <= newData.end;
  };

  const isStartDate = (date) => {
    return newData.start && date.getTime() === newData.start.getTime();
  };

  const isEndDate = (date) => {
    return newData.end && date.getTime() === newData.end.getTime();
  };

  const { daysInMonth, startingDayOfWeek } = getDaysInMonth(currentMonth);
  const monthName = currentMonth.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
  
  console.log(newData);
  return (
    <div className="relative w-full max-w-md mx-auto">
      <div className="mb-32" data-testid="daterangepicker">
        {/* Date Input Fields */}
        <div className="space-y-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-[#c44545] mb-2">Start Date</label>
            <input
              type="date"
              value={newData.start ? newData.start.toISOString().split('T')[0] : ''}
              onChange={(e) => handleInputChange('start', e.target.value)}
              className="w-full px-3 py-2 bg-[#1a1a1a] border-2 border-[#8c2e2e] text-white rounded-md focus:border-[#c44545] focus:outline-none minecraft-font"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-[#c44545] mb-2">End Date</label>
            <input
              type="date"
              value={newData.end ? newData.end.toISOString().split('T')[0] : ''}
              onChange={(e) => handleInputChange('end', e.target.value)}
              className="w-full px-3 py-2 bg-[#1a1a1a] border-2 border-[#8c2e2e] text-white rounded-md focus:border-[#c44545] focus:outline-none minecraft-font"
            />
          </div>
        </div>

        {/* Inline Calendar */}
        <div className="bg-[#2a2a2a] rounded-lg p-4 border border-[#8c2e2e]">
          {/* Calendar Header */}
          <div className="flex items-center justify-between mb-4">
            <Button
              size="sm"
              variant="light"
              onPress={goToPreviousMonth}
              className="text-white hover:bg-[#8c2e2e] min-w-0 w-8 h-8 p-1 bg-[#1a1a1a] border border-[#8c2e2e] hover:border-[#c44545] rounded-sm"
            >
              ←
            </Button>
            <h3 className="text-white font-semibold minecraft-font">{monthName}</h3>
            <Button
              size="sm"
              variant="light"
              onPress={goToNextMonth}
              className="text-white hover:bg-[#8c2e2e] min-w-0 w-8 h-8 p-1 bg-[#1a1a1a] border border-[#8c2e2e] hover:border-[#c44545] rounded-sm"
            >
              →
            </Button>
          </div>

          {/* Day Names */}
          <div className="grid grid-cols-7 gap-1 mb-2">
            {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
              <div key={day} className="text-center text-xs font-medium text-[#a0a0a0] py-1">
                {day}
              </div>
            ))}
          </div>

          {/* Calendar Grid */}
          <div className="grid grid-cols-7 gap-1">
            {/* Empty cells for days before month starts */}
            {Array.from({ length: startingDayOfWeek }, (_, i) => (
              <div key={`empty-${i}`} className="h-8"></div>
            ))}
            
            {/* Days of the month */}
            {Array.from({ length: daysInMonth }, (_, i) => {
              const day = i + 1;
              const date = new Date(currentMonth.getFullYear(), currentMonth.getMonth(), day);
              const isInRange = isDateInRange(date);
              const isStart = isStartDate(date);
              const isEnd = isEndDate(date);
              const isToday = date.toDateString() === new Date().toDateString();
              
              let bgColor = 'bg-[#1a1a1a]';
              let textColor = 'text-white';
              let borderColor = 'border-[#8c2e2e]';
              
              if (isStart || isEnd) {
                bgColor = 'bg-[#8c2e2e]';
                textColor = 'text-white';
                borderColor = 'border-[#c44545]';
              } else if (isInRange) {
                bgColor = 'bg-[#c44545]/20';
                textColor = 'text-white';
                borderColor = 'border-[#c44545]/40';
              } else if (isToday) {
                bgColor = 'bg-[#a83838]/30';
                textColor = 'text-white';
                borderColor = 'border-[#a83838]';
              }
              
              return (
                <button
                  key={day}
                  onClick={() => handleDateSelect(date)}
                  className={`
                    h-8 rounded text-sm font-medium transition-all duration-150
                    ${bgColor} ${textColor} ${borderColor}
                    hover:bg-[#c44545] hover:text-white hover:border-[#c44545]
                    border cursor-pointer minecraft-font
                    ${isStart || isEnd ? 'shadow-[2px_2px_0px_0px_rgba(0,0,0,0.8)]' : ''}
                  `}
                >
                  {day}
                </button>
              );
            })}
          </div>
        </div>
        
        {/* Custom Clear Button */}
        <div className="flex justify-center mt-4">
          <Button
            onPress={handleClear}
            className="bg-[#333333] hover:bg-[#8c2e2e] text-white transition-colors text-sm px-4 py-2 rounded-md"
            size="sm"
          >
            Clear Dates
          </Button>
        </div>
      </div>

      <div className="absolute bottom-0 left-0">
        <PreviousButton onClick={prevComponent} />
      </div>
      <div className="absolute bottom-0 right-0">
        <NextButton
          disabled={!newData?.start || !newData?.end}
          onClick={() => nextComponent(newData)}
          newData={newData}
        />
      </div>
    </div>
  );
}
