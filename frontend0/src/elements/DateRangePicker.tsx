import React from 'react'
import { Calendar as CalendarIcon } from "lucide-react"
import { DateRange } from "react-day-picker"
import { addDays, format } from "date-fns"

import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { Calendar } from "@/components/ui/calendar"
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover"
type ChildComponentProps = {
  handleBackToEventDetails: () => void
  handleNextTab: () => void
  handleDateRange: (arg0: DateRange) => void;
};
const DateRangePicker: React.FC<ChildComponentProps> = ({handleBackToEventDetails, handleDateRange, handleNextTab}) => {
    const [date, setDate] = React.useState< DateRange | undefined>({
        from: new Date(),
        to: new Date(),
      })
    const handleNext = () => {
      if (date && date.from && date.to) {
        handleDateRange(date);
        // handleNextTab();
      } else {
        console.error("Date range is not fully selected");
      }
    }
    return (
        <div className= 'flex flex-col justify-center items-center h-screen max-w-fit m-auto '>
          <h4 className="scroll-m-20 text-2xl font-semibold tracking-tight">
            Select Your Date Range.
        </h4>  
      <Popover>
        <PopoverTrigger className = 'mb-320px' asChild>
          <Button
            id="date"
            variant={"outline"}
            className={cn(
              "w-[300px] justify-start text-left font-normal",
              !date && "text-muted-foreground"
            )}
          >
            <CalendarIcon className="mr-2 h-4 w-4" />
            {date?.from ? (
              date.to ? (
                <>
                  {format(date.from, "LLL dd, y")} -{" "}
                  {format(date.to, "LLL dd, y")}
                </>
              ) : (
                format(date.from, "LLL dd, y")
              )
            ) : (
              <span>Pick a date</span>
            )}
          </Button>
        </PopoverTrigger>
        <PopoverContent className="w-auto p-0" align="center">
          <Calendar
            initialFocus
            mode="range"
            defaultMonth={date?.from}
            selected={date}
            onSelect={setDate}
            numberOfMonths={2}
          />
        </PopoverContent>
      </Popover>
      <div className = "flex justify-between w-full">< Button onClick= {handleBackToEventDetails} variant = "secondary">back</Button><Button onClick={handleNext} >Confirm</Button><Button variant = "secondary" onClick={handleNextTab}>Next</Button></div>
    </div>
    )
}

export default DateRangePicker