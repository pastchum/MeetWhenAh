"use client";

import React, { useState, useEffect, useRef, useCallback } from "react";

// Helper function to get time slot info from DOM element
function getTimeSlotFromElement(element: HTMLElement): TimeSlotInfo | null {
  // Look for box element with the expected ID format
  const boxElement = element.closest('[id^="box-"]');
  if (!boxElement) return null;

  const id = boxElement.id;
  const match = id.match(/^box-(.+)-(\d{4})$/);
  if (!match) return null;

  const [, dateStr, time] = match;
  // Convert ISO date string to local date format
  const date = new Date(dateStr);
  const localDateStr = date.toLocaleDateString("en-GB");

  return {
    date: localDateStr,
    time,
    element: boxElement as HTMLElement,
  };
}

// Helper function to get all time slots in rectangular selection
function getRectangularSelection(
  startSlot: TimeSlotInfo,
  endSlot: TimeSlotInfo,
  container: HTMLElement
): TimeSlotInfo[] {
  const selectedSlots: TimeSlotInfo[] = [];

  // Get all box elements in the container
  const allBoxes = container.querySelectorAll('[id^="box-"]');

  // Parse start and end times as numbers for comparison
  const startTime = parseInt(startSlot.time);
  const endTime = parseInt(endSlot.time);
  const minTime = Math.min(startTime, endTime);
  const maxTime = Math.max(startTime, endTime);

  // Parse start and end dates for comparison
  const startDate = new Date(startSlot.date.split("/").reverse().join("-"));
  const endDate = new Date(endSlot.date.split("/").reverse().join("-"));
  const minDate = new Date(Math.min(startDate.getTime(), endDate.getTime()));
  const maxDate = new Date(Math.max(startDate.getTime(), endDate.getTime()));

  allBoxes.forEach((box) => {
    const slotInfo = getTimeSlotFromElement(box as HTMLElement);
    if (!slotInfo) return;

    const slotTime = parseInt(slotInfo.time);
    const slotDate = new Date(slotInfo.date.split("/").reverse().join("-"));

    // Check if this slot falls within the rectangular selection
    const isInTimeRange = slotTime >= minTime && slotTime <= maxTime;
    const isInDateRange = slotDate >= minDate && slotDate <= maxDate;

    if (isInTimeRange && isInDateRange) {
      selectedSlots.push(slotInfo);
    }
  });

  return selectedSlots;
}

interface Coordinates {
  x: number;
  y: number;
}

interface DrawnArea {
  start: undefined | Coordinates;
  end: undefined | Coordinates;
}

interface TimeSlotInfo {
  date: string;
  time: string;
  element: HTMLElement;
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
  const mouseDownRef = useRef(false);
  const drawAreaRef = useRef<DrawnArea>({ start: undefined, end: undefined });
  const moveListenerRef = useRef<((e: MouseEvent | TouchEvent) => void) | null>(
    null
  );
  const [mouseDown, setMouseDown] = useState<boolean>(false);
  const [selection, setSelection] = useState<DOMRect | null>(null);
  const [drawArea, setDrawArea] = useState<DrawnArea>({
    start: undefined,
    end: undefined,
  });
  const [touchStartTime, setTouchStartTime] = useState<number>(0);
  const [lastTouchPosition, setLastTouchPosition] =
    useState<Coordinates | null>(null);
  const [isDragging, setIsDragging] = useState<boolean>(false);
  const [startSlot, setStartSlot] = useState<TimeSlotInfo | null>(null);
  const [endSlot, setEndSlot] = useState<TimeSlotInfo | null>(null);
  const [rectangularSelection, setRectangularSelection] = useState<
    TimeSlotInfo[]
  >([]);

  // Clean up function to remove all listeners
  const cleanupListeners = useCallback((): void => {
    console.log("🧹 Cleaning up listeners", {
      hasExistingMoveHandler: !!moveListenerRef.current,
    });

    if (moveListenerRef.current) {
      document.removeEventListener("mousemove", moveListenerRef.current);
      document.removeEventListener("touchmove", moveListenerRef.current);
      moveListenerRef.current = null;
      console.log("%c🧹 Cleaned up listeners", "color: #0ea5e9");
    }
  }, []);

  // Create move handler
  const createMoveHandler = useCallback(() => {
    const moveHandler = (e: MouseEvent | TouchEvent) => {
      // Log the initial call
      console.log("[MOVE] Move Handler Initial Call", {
        mouseDownRef: mouseDownRef.current,
        eventType: e.type,
        isDragging,
        hasDrawArea: !!drawArea.start,
      });

      if (!mouseDownRef.current) {
        console.log(
          "%c⚠️ Move Handler Aborted - mouseDown false",
          "color: #dc2626"
        );
        return;
      }

      // Get coordinates
      const event = "touches" in e ? e.touches[0] : e;
      const { pageX, pageY } = event;

      // Log current mouse position
      console.log("🖱️ Mouse Position:", {
        x: pageX,
        y: pageY,
        startPosition: drawArea.start,
      });

      // If not dragging, check if we should start
      if (!isDragging && drawArea.start) {
        const deltaX = Math.abs(pageX - drawArea.start.x);
        const deltaY = Math.abs(pageY - drawArea.start.y);

        console.log("📏 Drag Detection:", {
          deltaX,
          deltaY,
          threshold: 5,
          shouldStartDrag: deltaX > 5 || deltaY > 5,
        });

        if (deltaX > 5 || deltaY > 5) {
          setIsDragging(true);
        }
      }

      // Update selection box
      if (boxRef.current && drawArea.start) {
        const box = boxRef.current;
        const { start } = drawArea;

        const dimensions = {
          left: Math.min(start.x, pageX),
          top: Math.min(start.y, pageY),
          width: Math.abs(pageX - start.x),
          height: Math.abs(pageY - start.y),
        };

        console.log("📦 Selection Box Update:", {
          previous: {
            left: box.style.left,
            top: box.style.top,
            width: box.style.width,
            height: box.style.height,
          },
          new: dimensions,
          dragDistance: {
            x: pageX - start.x,
            y: pageY - start.y,
          },
        });

        // Update box dimensions
        box.style.left = `${dimensions.left}px`;
        box.style.top = `${dimensions.top}px`;
        box.style.width = `${dimensions.width}px`;
        box.style.height = `${dimensions.height}px`;
      }

      // Update draw area state
      setDrawArea((prev) => {
        const newArea = {
          ...prev,
          end: { x: pageX, y: pageY },
        };
        console.log("[DRAW] Draw Area Update:", {
          previous: prev,
          new: newArea,
        });
        return newArea;
      });

      // Update end slot and rectangular selection
      if (container.current) {
        const elementUnderMouse = document.elementFromPoint(
          pageX,
          pageY
        ) as HTMLElement;
        if (elementUnderMouse) {
          const endSlotInfo = getTimeSlotFromElement(elementUnderMouse);
          if (endSlotInfo && startSlot) {
            setEndSlot(endSlotInfo);
            const rectangularSlots = getRectangularSelection(
              startSlot,
              endSlotInfo,
              container.current
            );
            setRectangularSelection(rectangularSlots);
            console.log("[RECTANGULAR] Selection updated:", {
              startSlot,
              endSlot: endSlotInfo,
              selectedCount: rectangularSlots.length,
            });
          }
        }
      }

      // Prevent default
      e.preventDefault();
      e.stopPropagation();
    };

    moveListenerRef.current = moveHandler;
    return moveHandler;
  }, [isDragging, drawArea, boxRef, container, startSlot]);

  const handlePointerUp = useCallback(
    (e: MouseEvent | TouchEvent) => {
      console.log("%c☝️ Pointer Up", "color: #dc2626", {
        isDragging,
        selectionActive: !!selection,
        mouseDownRef: mouseDownRef.current,
      });

      mouseDownRef.current = false;
      setMouseDown(false);
      setIsDragging(false);
      setDrawArea({ start: undefined, end: undefined });
      setLastTouchPosition(null);

      // Clear rectangular selection states after a delay to allow Box components to process
      setTimeout(() => {
        setStartSlot(null);
        setEndSlot(null);
        setRectangularSelection([]);
      }, 100);

      if (boxRef.current) {
        boxRef.current.style.width = "0";
        boxRef.current.style.height = "0";
      }

      cleanupListeners();

      // Create and attach new move handler
      const moveHandler = createMoveHandler();
      document.addEventListener("mousemove", moveHandler, { capture: true });
      document.addEventListener("touchmove", moveHandler, { capture: true });

      // Attach pointer up handlers
      document.addEventListener("mousedown", handlePointerUp, {
        capture: true,
      });
      document.addEventListener("touchend", handlePointerUp, { capture: true });

      const wasQuickTap = "touches" in e && Date.now() - touchStartTime < 200;
      if (!isDragging && !wasQuickTap) {
        setSelection(null);
      }
    },
    [
      isDragging,
      touchStartTime,
      cleanupListeners,
      boxRef,
      selection,
      createMoveHandler,
    ]
  );

  const handlePointerDown = useCallback(
    (e: MouseEvent | TouchEvent) => {
      const event = "touches" in e ? e.touches[0] : e;
      const { pageX, pageY } = event;
      const containerElement = container.current;

      console.log("%c👇 Pointer Down", "color: #dc2626", {
        type: e.type,
        target: (e.target as HTMLElement).id,
        coordinates: { x: pageX, y: pageY },
      });

      if (!containerElement?.contains(e.target as HTMLElement)) {
        console.log("%c⚠️ Invalid target - not in container", "color: #dc2626");
        return;
      }

      // Clean up any existing listeners first
      cleanupListeners();

      // Set initial states
      mouseDownRef.current = true;
      setMouseDown(true);
      setIsDragging(false);

      // Get the time slot info from the target element
      const startSlotInfo = getTimeSlotFromElement(e.target as HTMLElement);
      setStartSlot(startSlotInfo);
      setEndSlot(startSlotInfo); // Initialize end slot to start slot
      setRectangularSelection(startSlotInfo ? [startSlotInfo] : []);

      // Set initial draw area
      const initialDrawArea = {
        start: { x: pageX, y: pageY },
        end: { x: pageX, y: pageY },
      };
      setDrawArea(initialDrawArea);

      console.log(
        "[INIT] Initial Draw Area Set",
        "color: #059669",
        initialDrawArea
      );

      // Initialize selection box
      if (boxRef.current) {
        const box = boxRef.current;
        box.style.left = `${pageX}px`;
        box.style.top = `${pageY}px`;
        box.style.width = "0";
        box.style.height = "0";
        console.log("[SELECTION] Selection Box Initialized");
      }

      // Create and attach new move handler
      const moveHandler = createMoveHandler();
      document.addEventListener("mousemove", moveHandler, { capture: true });
      document.addEventListener("touchmove", moveHandler, { capture: true });

      // Attach pointer up handlers
      document.addEventListener("mouseup", handlePointerUp, { capture: true });
      document.addEventListener("touchend", handlePointerUp, { capture: true });

      console.log("[EVENTS] Event Listeners Attached");

      if ("touches" in e) {
        setTouchStartTime(Date.now());
        setLastTouchPosition({ x: pageX, y: pageY });
        e.preventDefault();
      }
    },
    [container, createMoveHandler, handlePointerUp, cleanupListeners, boxRef]
  );

  // Attach pointer down listener to container
  useEffect(() => {
    const containerElement = container.current;
    if (containerElement) {
      containerElement.addEventListener("mousedown", handlePointerDown, {
        capture: true,
      });
      containerElement.addEventListener("touchstart", handlePointerDown, {
        capture: true,
      });

      return () => {
        containerElement.removeEventListener("mousedown", handlePointerDown);
        containerElement.removeEventListener("touchstart", handlePointerDown);
        cleanupListeners();
      };
    }
  }, [container, handlePointerDown, cleanupListeners]);

  // Update selection box when drawing
  useEffect(() => {
    if (isDragging && drawArea.start && drawArea.end && boxRef.current) {
      const box = boxRef.current;
      const { start, end } = drawArea;

      // Calculate dimensions
      const left = Math.min(start.x, end.x);
      const top = Math.min(start.y, end.y);
      const width = Math.abs(end.x - start.x);
      const height = Math.abs(end.y - start.y);

      // Update box position and size
      box.style.left = `${left}px`;
      box.style.top = `${top}px`;
      box.style.width = `${width}px`;
      box.style.height = `${height}px`;

      setSelection(box.getBoundingClientRect());
    }
  }, [drawArea, isDragging, boxRef]);

  return {
    selection,
    rectangularSelection,
    startSlot,
    endSlot,
    isDragging,
  };
}
