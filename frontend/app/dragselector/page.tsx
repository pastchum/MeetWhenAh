'use client'

import React, { useRef, useContext, createContext, forwardRef, ReactNode, useState } from 'react';
import useSelected from '@/components/dragselector/useselected';
import useAreaSelection from '@/components/dragselector/useareaselection';

const SelectionContext = React.createContext<DOMRect | null>(null);

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
function Box() {
  const ref = React.useRef(null);
  const selection = React.useContext(SelectionContext);
  const isSelected = useSelected(ref, selection);
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

const Container = forwardRef<HTMLElement, ContainerProps>(({ columns, rows }, ref) => {
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
export default function Home() {  

  const selectContainerRef = React.useRef<HTMLElement | null>(null);
  const selection = useAreaSelection({ container: selectContainerRef });
  const [selectedElements, setSelectedElements] = useState<Set<number>>(new Set());
  const rows = 12;
  const columns = 12;

  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24 w-screen">
      <head>
        <script src="https://telegram.org/js/telegram-web-app.js"></script>
      </head>
      <div>
        <SelectionContext.Provider value={selection}>
          <Container ref={selectContainerRef} columns={columns} rows={rows}/>
        </SelectionContext.Provider>
        {/* <pre
          style={{
            display: "inline-block",
            lineHeight: "1.4",
            background: "rgba(0,0,0,0.05)",
            padding: "1rem",
            borderRadius: ".5rem",
            margin: "4rem",
            fontSize: "1rem"
          }}
        >
          selection: {JSON.stringify(selection, null, 2)}
        </pre> */}
      </div>
    </main>
  );
}
