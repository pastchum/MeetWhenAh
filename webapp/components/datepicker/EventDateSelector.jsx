import { DateRangePicker, Button } from "@nextui-org/react";
import NextButton from "@/components/datepicker/NextButton";
import PreviousButton from "@/components/datepicker/PreviousButton";
import { today, getLocalTimeZone, CalendarDate } from "@internationalized/date";
import { useState } from "react";

export default function EventDateSelector({
  prevComponent,
  nextComponent,
  initialData = null
}) {
  const [newData, setNewData] = useState(() => {
    if (initialData?.start && initialData?.end) {
      try {
        // If initialData has date objects, use them
        if (typeof initialData.start === 'object' && initialData.start.calendar) {
          return {
            start: initialData.start,
            end: initialData.end
          };
        }
        // If initialData has string dates, convert them
        if (typeof initialData.start === 'string') {
          const startDate = new Date(initialData.start);
          const endDate = new Date(initialData.end);
          return {
            start: new CalendarDate(startDate.getFullYear(), startDate.getMonth() + 1, startDate.getDate()),
            end: new CalendarDate(endDate.getFullYear(), endDate.getMonth() + 1, endDate.getDate())
          };
        }
      } catch (error) {
        console.warn('Error parsing initial dates:', error);
      }
    }
    
    // Start with today as default like the original
    return {
      start: today(getLocalTimeZone()),
      end: today(getLocalTimeZone()),
    };
  });

  const handleClear = () => {
    setNewData({
      start: today(getLocalTimeZone()),
      end: today(getLocalTimeZone()),
    });
  };

  const handleDateChange = (value) => {
    if (value) {
      setNewData(value);
    }
  };
  
  console.log(newData);
  return (
    <div className="relative w-full max-w-md mx-auto">
      <div className="mb-32" data-testid="daterangepicker">
        <DateRangePicker
          isRequired
          labelPlacement="inside"
          label="Event Date Range"
          description="Choose the start and end dates for your event"
          value={newData}
          onChange={handleDateChange}
          shouldCloseOnSelect={false}
          classNames={{
            base: "w-full minecraft-font",
            inputWrapper: [
              "bg-[#1a1a1a]", 
              "border-2", 
              "border-[#8c2e2e]",
              "text-white",
              "hover:bg-[#1a1a1a]",
              "focus-within:!bg-[#1a1a1a]",
              "focus-within:!border-[#c44545]",
              "min-h-[60px]",
              "minecraft-font",
              "rounded-md"
            ],
            input: [
              "text-white", 
              "placeholder:text-[#a0a0a0]",
              "minecraft-font"
            ],
            label: "text-[#c44545] minecraft-font font-bold",
            description: "text-[#a0a0a0] minecraft-font text-xs",
            calendar: [
              "bg-[#2a2a2a]",
              "border-0",
              "minecraft-font"
            ],
            calendarContent: [
              "bg-[#1a1a1a]",
              "[&_[data-range-highlight=true]]:bg-[#c44545]/20",
              "[&_[data-range-highlight=true]]:m-0.5",
              "minecraft-font",
              "rounded-md"
            ],
            popoverContent: [
              "bg-[#2a2a2a] border-0",
              "minecraft-font",
              "rounded-lg",
              "transition-all duration-200 ease-in-out",
              "data-[entering=true]:animate-in data-[entering=true]:fade-in-0 data-[entering=true]:zoom-in-95",
              "data-[exiting=true]:animate-out data-[exiting=true]:fade-out-0 data-[exiting=true]:zoom-out-95"
            ],
            selectorButton: [
              "text-white", 
              "hover:bg-[#8c2e2e]",
              "min-w-[32px]",
              "w-[32px]",
              "h-[32px]",
              "p-1",
              "text-xs",
              "border-2",
              "border-[#8c2e2e]",
              "bg-[#1a1a1a]",
              "hover:border-[#c44545]",
              "rounded-full",
              "minecraft-font"
            ],
            calendarHeaderWrapper: "bg-[#1a1a1a] border-b-2 border-[#8c2e2e] minecraft-font",
            calendarHeader: "bg-[#1a1a1a] text-white minecraft-font",
            prevButton: "text-white hover:bg-[#8c2e2e] min-w-0 w-6 h-6 p-1 bg-[#1a1a1a] border border-[#8c2e2e] hover:border-[#c44545] minecraft-font rounded-sm",
            nextButton: "text-white hover:bg-[#8c2e2e] min-w-0 w-6 h-6 p-1 bg-[#1a1a1a] border border-[#8c2e2e] hover:border-[#c44545] minecraft-font rounded-sm",
            gridHeader: "bg-[#2a2a2a] border-b border-[#8c2e2e] minecraft-font",
            gridHeaderRow: "bg-[#2a2a2a] minecraft-font",
            gridHeaderCell: "text-[#a0a0a0] bg-[#2a2a2a] minecraft-font text-xs font-bold border-r border-[#8c2e2e]/30 last:border-r-0"
          }}
        />
        
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
