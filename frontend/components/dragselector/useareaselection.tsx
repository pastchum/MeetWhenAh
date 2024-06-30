'use client'

import React, { useState, useRef, useEffect } from 'react';

interface Coordinates {
  x: number;
  y: number;
}
interface DrawnArea {
  start: undefined | Coordinates;
  end: undefined | Coordinates;
}
interface UseAreaSelectionProps {
  container: React.RefObject<HTMLElement> | undefined;
}

const boxNode = document.createElement("div");
boxNode.style.position = "fixed";
boxNode.style.background = "hsl(206deg 100% 50% / 5%)";
boxNode.style.boxShadow = "inset 0 0 0 2px hsl(206deg 100% 50% / 50%)";
boxNode.style.borderRadius = "2px";
boxNode.style.pointerEvents = "none";
boxNode.style.mixBlendMode = "multiply";

export default function useAreaSelection({
  container = { current: document.body }
}: UseAreaSelectionProps) {
  const boxRef = React.useRef<HTMLDivElement>(boxNode);
  const boxElement = boxRef;
  const [mouseDown, setMouseDown] = React.useState<boolean>(false);
  
  const [selection, setSelection] = React.useState<DOMRect | null>(null);
  const [drawArea, setDrawArea] = React.useState<DrawnArea>({
    start: undefined,
    end: undefined
  });

  const handleMouseMove = (e: MouseEvent | TouchEvent) => {
    const clientX = (e as MouseEvent).clientX ?? (e as TouchEvent).touches[0].clientX;
    const clientY = (e as MouseEvent).clientY ?? (e as TouchEvent).touches[0].clientY;

    document.body.style.userSelect = "none";
    setDrawArea((prev) => ({
      ...prev,
      end: {
        x: clientX,
        y: clientY
      }
    }));
  };

  const handleMouseDown = (e: MouseEvent | TouchEvent) => {
    const clientX = (e as MouseEvent).clientX ?? (e as TouchEvent).touches[0].clientX;
    const clientY = (e as MouseEvent).clientY ?? (e as TouchEvent).touches[0].clientY;
    const containerElement = container.current;

    setMouseDown(true);

    if (
      containerElement &&
      containerElement.contains(e.target as HTMLElement)
    ) {
      document.addEventListener("mousemove", handleMouseMove);
      document.addEventListener("touchmove", handleMouseMove);
      setDrawArea({
        start: {
          x: clientX,
          y: clientY
        },
        end: {
          x: clientX,
          y: clientY
        }
      });
    }
  };

  const handleMouseUp = (e: MouseEvent | TouchEvent) => {
    document.body.style.userSelect = "initial";
    document.removeEventListener("mousemove", handleMouseMove);
    document.removeEventListener("touchmove", handleMouseMove);
    setMouseDown(false);
    // set selection
  };

  React.useEffect(() => {
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

  React.useEffect(() => {
    const { start, end } = drawArea;
    if (start && end && boxElement.current) {
      drawSelectionBox(boxElement.current, start, end);
      setSelection(boxElement.current.getBoundingClientRect());
    }
  }, [drawArea, boxElement]);

  React.useEffect(() => {
    const containerElement = container.current;
    const selectionBoxElement = boxElement.current;
    if (containerElement && selectionBoxElement) {
      if (mouseDown) {
        if (!document.body.contains(selectionBoxElement)) {
          containerElement.appendChild(selectionBoxElement);
        }
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
