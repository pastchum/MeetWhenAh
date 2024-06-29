import { DateRangePicker } from "@nextui-org/react";
import NextButton from '@/components/datepicker/NextButton'
import PreviousButton from '@/components/datepicker/PreviousButton'
import {today, parseDate, getLocalTimeZone} from "@internationalized/date";
import { useState } from 'react';


export default function CustomDateRangePicker({ prevComponent, nextComponent }) {
    const [value, setValue] = useState({
        start: today(getLocalTimeZone()),
        end: today(getLocalTimeZone())
    });


    return(
        <div className="relative space-y-14 w-[80vw] sm:w-[60vw]">
            <div className=''>
                <DateRangePicker 
                    isRequired 
                    labelPlacement="inside"
                    label="Date Range"
                    description="Please enter the date range for your event"
                    value={value}
                    onChange={setValue}
                />
            </div>
            
            <div className="absolute left-0">
                <PreviousButton onClick={prevComponent} />

            </div>
            <div className="absolute right-0">

                <NextButton onClick={nextComponent} />
            </div>
        </div> 
    )
     
    
}