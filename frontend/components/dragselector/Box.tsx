import UseSelected from '@/components/dragselector/UseSelected';
import { createContext, useRef, useContext } from 'react'
import { SelectionContext } from '@/components/dragselector/DragSelector'

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



export default function Box() {
    const ref = useRef(null);
    const selection = useContext(SelectionContext);
    const isSelected = UseSelected(ref, selection);
    return (
        <div
            ref={ref}
            style={{
                ...boxStyles,
                ...(isSelected && {
                    boxShadow: "inset 0 0 0 .25rem hsl(206deg 100% 50%)"
                })
        }}
        />
    );
}
  