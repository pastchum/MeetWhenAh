import { DateRangePicker } from "@nextui-org/react";
import NextButton from '@/components/datepicker/NextButton'
import PreviousButton from '@/components/datepicker/PreviousButton'
import {today, CalendarDate, DateFormatter, getLocalTimeZone} from "@internationalized/date";
import { useState } from 'react';


export default function CustomDateRangePicker({ prevComponent, nextComponent }) {
    const formatter = new DateFormatter('en-GB');
    const [newData, setNewData] = useState({
        start: today(getLocalTimeZone()),
        end: today(getLocalTimeZone())
    });
    console.log(newData);
    return(
        <div className="relative space-y-14 w-[80vw] sm:w-[60vw]">
            <div className=''>
                <DateRangePicker 
                    isRequired 
                    labelPlacement="inside"
                    label="Date Range"
                    description="Please enter the date range for your event"
                    value={newData}
                    onChange={setNewData}
                />
            </div>
            
            <div className="absolute left-0">
                <PreviousButton onClick={prevComponent} />
            </div>
            <div className="absolute right-0">
                <NextButton onClick={nextComponent} newData={newData}/>
            </div>
        </div> 
    )
     
    
}