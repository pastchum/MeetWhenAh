import { useRef, useContext, createContext, forwardRef, ReactNode, useState, Fragment, useEffect} from 'react';
import Box from '@/components/dragselector/Box'
import useAreaSelection from '@/components/dragselector/useAreaSelection';
import CustomDateTimeSet from '@/components/dragselector/CustomDateTimeSet';

  
interface ContainerProps {
  startDate: Date;
  numberOfDays: number;
  appendMode: boolean;
  removeNight: boolean
}
  
const Container = forwardRef<HTMLDivElement, ContainerProps>(({ startDate, numberOfDays, appendMode, removeNight}, ref) => {
  const [timeIntervals, setTimeIntervals] = useState<string[]>([]);
  const [dates, setDates] = useState<Date[]>([]);
  const generateTimeIntervals = () => {
    const intervals = [];
    if (removeNight) {
      for (let hour = 6; hour < 22; hour++) {
        for (let minute = 0; minute < 60; minute += 30) {
          intervals.push(`${hour.toString().padStart(2, '0')}${minute.toString().padStart(2, '0')}`);
        }
      }
    }
    else {
      for (let hour = 0; hour < 24; hour++) {
        for (let minute = 0; minute < 60; minute += 30) {
          intervals.push(`${hour.toString().padStart(2, '0')}${minute.toString().padStart(2, '0')}`);
        }
      }
    }
    
    setTimeIntervals(intervals);
  };

  const generateDates = () => {
    const dateList = [];
    for (let i = 0; i < numberOfDays; i++) {
      const date = new Date(startDate);
      date.setDate(date.getDate() + i);
      dateList.push(date);
    }
    setDates(dateList);
  };

  useEffect(() => {
    generateTimeIntervals();  
  }, [removeNight])

  useEffect(() => {
    console.log(startDate)
    setDates([])
    generateDates();
  }, [startDate])

  const finalContainerStyles = {
    gridTemplateColumns: `repeat(${numberOfDays+1}, 2rem)`,
    gridTemplateRows: `repeat(${timeIntervals.length}, 1rem)`,
  };

  return (
    <div ref={ref} className="grid gap-y-0.5 gap-x-3 w-screen max-w-full bg-transparent items-center justify-center" style={finalContainerStyles}>
      {/* Empty top-left cell */}
      <div className="flex justify-center items-center text-sm font-bold"></div>

        {/* Date labels */}
        {dates.map((date) => (
          <div key={date.toISOString()} className="flex justify-center items-center text-sm sm:text-sm font-bold">
            {date.toLocaleDateString('en-GB', { month: 'numeric', day: 'numeric' })}
          </div>
        ))}

        {/* Time labels and boxes */}
        {timeIntervals.map((time) => (
          <Fragment key={time}>
            {/* Time label */}
            <div className="flex justify-center items-center text-sm font-bold ">{time}</div>

            {/* Boxes for each date */}
            {dates.map((date) => (
              <Box key={`${date.toISOString()}-${time}`} date={date} time={time} appendMode={appendMode} />
            ))}
        </Fragment>
        ))}
    </div>
  );
  });


export interface DateTime {
  date: string;
  time: string;
}

interface SelectionContextType {
  selectionRect: DOMRect | null;
  selectedElements: CustomDateTimeSet;
  setSelectedElements: React.Dispatch<React.SetStateAction<CustomDateTimeSet>>;
  
}

const defaultSetSelectedElements: React.Dispatch<React.SetStateAction<CustomDateTimeSet>> = () => new Set();
export const SelectionContext = createContext<SelectionContextType>({selectionRect: null,
                                                                    selectedElements: new CustomDateTimeSet(), 
                                                                    setSelectedElements:defaultSetSelectedElements,
                                                                    })


interface DragSelectorProps {
  removeNight: boolean
  startDate: Date,
  numDays: number,
  selectedElements: CustomDateTimeSet,
  setSelectedElements: React.Dispatch<React.SetStateAction<CustomDateTimeSet>>;
}



export default function DragSelector( {removeNight, startDate, numDays, selectedElements, setSelectedElements}:DragSelectorProps ) {
    const selectContainerRef = useRef<HTMLDivElement | null>(null);
    const selectionBoxRef = useRef<HTMLDivElement | null>(null);
    const [appendMode, setAppendMode] = useState<boolean>(false);
    const selection = useAreaSelection({ container: selectContainerRef, selectionBox: selectionBoxRef, appendMode: appendMode, setAppendMode: setAppendMode});

    
    useEffect(() => {
      console.log(selectedElements)
    }, [selectedElements])
  
    
    
    return (
        <div>
            <SelectionContext.Provider value={{selectionRect: selection, selectedElements: selectedElements, setSelectedElements: setSelectedElements}}>
                <Container removeNight={removeNight} ref={selectContainerRef} startDate={startDate} numberOfDays={numDays} appendMode={appendMode}  />
                <div ref={selectionBoxRef} className="fixed bg-custom-blue shadow-custom-inset rounded pointer-events-none mix-blend-multiply"></div>
            </SelectionContext.Provider>
      </div>

    )

}