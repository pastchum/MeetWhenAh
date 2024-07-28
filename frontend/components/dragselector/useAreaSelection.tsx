'use client';

import React, { useState, useEffect } from 'react';

interface Coordinates {
  x: number;
  y: number;
}
interface DrawnArea {
  start: undefined | Coordinates;
  end: undefined | Coordinates;
}
interface useAreaSelectionProps {
  container: React.RefObject<HTMLElement> | undefined;
  selectionBox: React.RefObject<HTMLElement> | undefined;
  appendMode: boolean;
  setAppendMode: React.Dispatch<React.SetStateAction<boolean>>;
}

export default function useAreaSelection({
    container = { current: document.body },
    selectionBox = { current: null },
    appendMode = false,
    setAppendMode = () => false,
  }: useAreaSelectionProps) {
  const boxRef = selectionBox;
  const boxElement = boxRef;
  const [mouseDown, setMouseDown] = useState<boolean>(false);
  const [selection, setSelection] = useState<DOMRect | null>(null);
  const [drawArea, setDrawArea] = useState<DrawnArea>({
    start: undefined,
    end: undefined
  });

  const handleMouseMove = (e: MouseEvent | TouchEvent) => {
    const pageX = (e as MouseEvent).pageX ?? (e as TouchEvent).touches[0].pageX;
    const pageY = (e as MouseEvent).pageY ?? (e as TouchEvent).touches[0].pageY;
    setDrawArea((prev) => ({
      ...prev,
      end: {
        x: pageX,
        y: pageY
      }
    }));
  };

  const handleMouseDown = (e: MouseEvent | TouchEvent) => {
    const pageX = (e as MouseEvent).pageX ?? (e as TouchEvent).touches[0].pageX;
    const pageY = (e as MouseEvent).pageY ?? (e as TouchEvent).touches[0].pageY;
    e.preventDefault();
    const containerElement = container.current;

    setAppendMode(false);
    if (e.ctrlKey || e.altKey || e.shiftKey ) {
      setAppendMode(true);
    } 
    setMouseDown(true);
    
    if (
      containerElement &&
      containerElement.contains(e.target as HTMLElement)
    ) {
      document.addEventListener("mousemove", handleMouseMove);
      document.addEventListener("touchmove", handleMouseMove);
      setDrawArea({
        start: {
          x: pageX,
          y: pageY
        },
        end: {
          x: pageX,
          y: pageY
        }
      });
    }
  };

  const handleMouseUp = (e: MouseEvent | TouchEvent) => {
    document.removeEventListener("mousemove", handleMouseMove);
    document.removeEventListener("touchmove", handleMouseMove);
    setMouseDown(false);
    setDrawArea({
      start: undefined,
      end: undefined
    });

  };

  useEffect(() => {
    const containerElement = container.current;
    if (containerElement) {
      containerElement.addEventListener("mousedown", handleMouseDown);
      containerElement.addEventListener("touchstart", handleMouseDown);
      document.addEventListener("mouseup", handleMouseUp);
      document.addEventListener("touchend", handleMouseUp);

      return () => {
        containerElement.removeEventListener("mousedown", handleMouseDown);
        containerElement.removeEventListener("touchstart", handleMouseDown);
        document.removeEventListener("mouseup", handleMouseUp);
        document.removeEventListener("touchend", handleMouseUp);
      };
    }
  }, [container]);

  useEffect(() => {
    const { start, end } = drawArea;
    if (start && end && boxElement.current) {
      drawSelectionBox(boxElement.current, start, end);
      setSelection(boxElement.current.getBoundingClientRect());
    }
  }, [drawArea, boxElement]);

  useEffect(() => {
    const containerElement = container.current;
    const selectionBoxElement = boxElement.current;
    if (containerElement && selectionBoxElement) {
      if (mouseDown) {
        containerElement.appendChild(selectionBoxElement);
        // if (!document.body.contains(selectionBoxElement)) {
        //   containerElement.appendChild(selectionBoxElement);
        // }
      } else {
        if (containerElement.contains(selectionBoxElement)) {
          containerElement.removeChild(selectionBoxElement);
        }
      }
    }
  }, [mouseDown, container, boxElement]);

  return selection;
}

function drawSelectionBox(
  boxElement: HTMLElement,
  start: Coordinates,
  end: Coordinates
): void {
  const b = boxElement;
  if (end.x > start.x) {
    b.style.left = start.x + "px";
    b.style.width = end.x - start.x + "px";
  } else {
    b.style.left = end.x + "px";
    b.style.width = start.x - end.x + "px";
  }

  if (end.y > start.y) {
    b.style.top = start.y + "px";
    b.style.height = end.y - start.y + "px";
  } else {
    b.style.top = end.y + "px";
    b.style.height = start.y - end.y + "px";
  }
}
