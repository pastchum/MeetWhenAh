import useSelected from '@/components/dragselector/useSelected';
import { useRef, useContext, useEffect } from 'react'
import { SelectionContext, DateTime } from '@/components/dragselector/DragSelector'
import CustomDateTimeSet from '@/components/dragselector/CustomDateTimeSet';

interface BoxProps {
    date: Date;
    time: string;
    appendMode: boolean;
  }

const boxStyles = {
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    background: "#fff",
    width: "2rem",
    height: "1rem",
    borderRadius: "0.5rem",
    transition: "all 200ms ease-in-out"
};


export default function Box({ date, time, appendMode }: BoxProps) {
    const newDateTime:DateTime = { date: date.toString(),
        time: time 
    }
    const ref = useRef<HTMLDivElement>(null);
    const { selectionRect, selectedElements, setSelectedElements } = useContext(SelectionContext);

    const isAlreadySelected = selectedElements.has(newDateTime);
    const isSelected = useSelected(ref, selectionRect, isAlreadySelected, appendMode);


    useEffect(() => {
        
        if (isSelected) {
            setSelectedElements((prevElements: CustomDateTimeSet): CustomDateTimeSet => {
                const newSet = new CustomDateTimeSet(prevElements);
                newSet.add(newDateTime);
                return newSet;
            });
        } 
        else{
            setSelectedElements((prevElements: CustomDateTimeSet): CustomDateTimeSet => {
                const newSet = new CustomDateTimeSet();
                newSet.delete(newDateTime);
                return newSet;
            });
        }
        
    }, [isSelected]);

    
    return (
        <div
            ref={ref}
            className="flex justify-center items-center bg-white w-8 h-4 rounded transition-all duration-200 ease-in-out"
            style={{
                ...(isSelected && {
                    boxShadow: "inset 0 0 0 .25rem hsl(206deg 100% 50%)"
                })
        }}
        />
    );
}
  