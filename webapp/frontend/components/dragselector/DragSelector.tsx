import {
  useRef,
  createContext,
  forwardRef,
  useState,
  Fragment,
  useEffect,
  useCallback,
} from "react";
import Box from "@/components/dragselector/Box";
import useAreaSelection from "@/components/dragselector/useAreaSelection";
import CustomDateTimeSet from "@/components/dragselector/CustomDateTimeSet";

interface ContainerProps {
  startDate: Date;
  numberOfDays: number;
  appendMode: boolean;
  removeNight: boolean;
}

const Container = forwardRef<HTMLDivElement, ContainerProps>(function Component(
  { startDate, numberOfDays, appendMode, removeNight },
  ref
) {
  const [timeIntervals, setTimeIntervals] = useState<string[]>([]);
  const [dates, setDates] = useState<Date[]>([]);
  const generateTimeIntervals = useCallback(() => {
    const intervals = [];
    if (removeNight) {
      for (let hour = 6; hour < 22; hour++) {
        for (let minute = 0; minute < 60; minute += 30) {
          intervals.push(
            `${hour.toString().padStart(2, "0")}${minute
              .toString()
              .padStart(2, "0")}`
          );
        }
      }
    } else {
      for (let hour = 0; hour < 24; hour++) {
        for (let minute = 0; minute < 60; minute += 30) {
          intervals.push(
            `${hour.toString().padStart(2, "0")}${minute
              .toString()
              .padStart(2, "0")}`
          );
        }
      }
    }

    setTimeIntervals(intervals);
  }, [removeNight]);

  const generateDates = useCallback(() => {
    const dateList = [];
    for (let i = 0; i < numberOfDays; i++) {
      const date = new Date(startDate);
      date.setDate(date.getDate() + i);
      dateList.push(date);
    }
    setDates(dateList);
  }, [startDate, numberOfDays]);

  useEffect(() => {
    generateTimeIntervals();
  }, [generateTimeIntervals]);

  useEffect(() => {
    console.log(startDate);
    setDates([]);
    generateDates();
  }, [generateDates, startDate]);

  const finalContainerStyles = {
    gridTemplateColumns: `minmax(3rem, auto) repeat(${numberOfDays}, minmax(2.5rem, 1fr))`,
    gridTemplateRows: `repeat(${timeIntervals.length}, minmax(1.5rem, auto))`,
  };

  return (
    <div className="relative w-full max-w-screen-lg mx-auto px-2 overflow-x-auto">
      <div
        ref={ref}
        className="grid gap-y-1 gap-x-2 bg-transparent items-center justify-start min-w-fit"
        style={finalContainerStyles}
      >
        {/* Time column header */}
        <div className="sticky left-0 top-0 z-10 bg-zinc-200 dark:bg-zinc-800 py-2 px-1 text-center font-bold">
          Time
        </div>

        {/* Date headers */}
        {dates.map((date) => (
          <div
            key={date.toISOString()}
            className="py-2 px-1 text-center font-bold text-sm whitespace-nowrap"
          >
            {date.toLocaleDateString("en-GB", {
              weekday: "short",
              month: "numeric",
              day: "numeric",
            })}
          </div>
        ))}

        {/* Time labels and boxes */}
        {timeIntervals.map((time) => (
          <Fragment key={time}>
            {/* Time label - sticky on mobile scroll */}
            <div className="sticky left-0 bg-zinc-200 dark:bg-zinc-800 py-1 px-2 text-sm font-medium text-center">
              {`${time.slice(0, 2)}:${time.slice(2)}`}
            </div>

            {/* Boxes for each date */}
            {dates.map((date) => (
              <Box
                key={`${date.toISOString()}-${time}`}
                date={date}
                time={time}
                appendMode={appendMode}
              />
            ))}
          </Fragment>
        ))}
      </div>
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

const defaultSetSelectedElements: React.Dispatch<
  React.SetStateAction<CustomDateTimeSet>
> = () => new Set();
export const SelectionContext = createContext<SelectionContextType>({
  selectionRect: null,
  selectedElements: new CustomDateTimeSet(),
  setSelectedElements: defaultSetSelectedElements,
});

interface DragSelectorProps {
  removeNight: boolean;
  startDate: Date;
  numDays: number;
  selectedElements: CustomDateTimeSet;
  setSelectedElements: React.Dispatch<React.SetStateAction<CustomDateTimeSet>>;
}

export default function DragSelector({
  removeNight,
  startDate,
  numDays,
  selectedElements,
  setSelectedElements,
}: DragSelectorProps) {
  const selectContainerRef = useRef<HTMLDivElement | null>(null);
  const selectionBoxRef = useRef<HTMLDivElement | null>(null);
  const [appendMode, setAppendMode] = useState<boolean>(false);

  // Log component initialization and ref setup
  useEffect(() => {
    console.log("%c🎯 DragSelector Initialized", "color: #0ea5e9", {
      removeNight,
      startDate: startDate.toISOString(),
      numDays,
      totalSelected: selectedElements.size(),
      containerRef: {
        exists: !!selectContainerRef.current,
        className: selectContainerRef.current?.className,
        id: selectContainerRef.current?.id,
        rect: selectContainerRef.current?.getBoundingClientRect(),
      },
      selectionBoxRef: {
        exists: !!selectionBoxRef.current,
        className: selectionBoxRef.current?.className,
        style: selectionBoxRef.current?.style.cssText,
      },
    });
  }, [removeNight, startDate, numDays, selectedElements]);

  // Log when refs are updated
  useEffect(() => {
    console.log("%c📌 Container Ref Update", "color: #059669", {
      containerExists: !!selectContainerRef.current,
      containerClass: selectContainerRef.current?.className,
      containerRect: selectContainerRef.current?.getBoundingClientRect(),
    });
  }, []);

  // Log selection box ref updates
  useEffect(() => {
    console.log("%c🎨 Selection Box Ref Update", "color: #8b5cf6", {
      exists: !!selectionBoxRef.current,
      style: selectionBoxRef.current?.style.cssText,
      rect: selectionBoxRef.current?.getBoundingClientRect(),
    });
  }, []);

  const selection = useAreaSelection({
    container: selectContainerRef,
    selectionBox: selectionBoxRef,
    appendMode: appendMode,
    setAppendMode: setAppendMode,
  });

  // Log selection updates
  useEffect(() => {
    if (selection) {
      console.log("%c📍 Selection Updated", "color: #8b5cf6", {
        selectionRect: {
          left: Math.round(selection.left),
          top: Math.round(selection.top),
          width: Math.round(selection.width),
          height: Math.round(selection.height),
        },
        appendMode,
      });
    }
  }, [selection, appendMode]);

  return (
    <div className="relative">
      <SelectionContext.Provider
        value={{
          selectionRect: selection,
          selectedElements: selectedElements,
          setSelectedElements: setSelectedElements,
        }}
      >
        <Container
          removeNight={removeNight}
          ref={selectContainerRef}
          startDate={startDate}
          numberOfDays={numDays}
          appendMode={appendMode}
        />
        <div
          ref={selectionBoxRef}
          className="fixed bg-blue-500/20 border-2 border-blue-600/40 rounded pointer-events-none"
          style={{ zIndex: 50 }}
        />
      </SelectionContext.Provider>
    </div>
  );
}
