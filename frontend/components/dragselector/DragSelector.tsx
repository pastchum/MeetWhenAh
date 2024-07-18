import { useRef, useContext, createContext, forwardRef, ReactNode, useState } from 'react';
import Box from '@/components/dragselector/Box'
import useAreaSelection from '@/components/dragselector/useareaselection';


const containerStyles = {
    display: "grid",
    gridTemplateColumns: "",
    flexWrap: "wrap",
    gap: "10px",
    width: "100vw",
    maxWidth: "100%",
    margin: "10ch auto",
    background: "#eee",
    padding: "4rem",
    alignItems: "center",
    justifyContent: "center",
    overflow: "scroll",
    border: ".25rem dashed #aaa",
    borderRadius: "1rem",
  };

  
interface ContainerProps {
    columns: number;
    rows: number;
}
  
const Container = forwardRef<HTMLDivElement, ContainerProps>(({ columns, rows }, ref) => {
    const boxes = Array.from({ length: columns * rows }, (_, i) => i + 1);
    const finalContainerStyles = {
      ...containerStyles,
      gridTemplateColumns: `repeat(${columns}, 2rem)`,
    }
    return (
      <div ref={ref} style={finalContainerStyles}>
        {boxes.map((number) => (
          <Box />
        ))}
      </div>
    );
  });



export const SelectionContext = createContext<DOMRect | null>(null);

export default function DragSelector() {
    const selectContainerRef = useRef<HTMLDivElement | null>(null);
    const selectionBoxRef = useRef<HTMLDivElement | null>(null);
    const selection = useAreaSelection({ container: selectContainerRef, selectionBox: selectionBoxRef});


    const [selectedElements, setSelectedElements] = useState<Set<number>>(new Set());
    const rows = 12;
    const columns = 12;

    return (
        <div>
            <SelectionContext.Provider value={selection}>
                <Container ref={selectContainerRef} columns={columns} rows={rows}/>
                <div ref={selectionBoxRef} className="fixed bg-custom-blue shadow-custom-inset rounded pointer-events-none mix-blend-multiply"></div>
            </SelectionContext.Provider>
      </div>

    )

}