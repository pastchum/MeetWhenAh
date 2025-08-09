import { useContext, useEffect, useState, useCallback } from "react";
import { SelectionContext } from "./DragSelector";
import CustomDateTimeSet from "./CustomDateTimeSet";

interface BoxProps {
  date: Date;
  time: string;
  appendMode: boolean;
}

export default function Box({ date, time, appendMode }: BoxProps) {
  const { selectionRect, selectedElements, setSelectedElements } =
    useContext(SelectionContext);
  const [isSelected, setIsSelected] = useState(false);
  const [isBeingSelected, setIsBeingSelected] = useState(false);

  // Check if this box is already selected
  const checkIsSelected = useCallback(() => {
    const dateTime = { date: date.toLocaleDateString("en-GB"), time };
    return selectedElements.has(dateTime);
  }, [date, time, selectedElements]);

  // Update selection state when selectedElements changes
  useEffect(() => {
    setIsSelected(checkIsSelected());
  }, [checkIsSelected]);

  useEffect(() => {
    const boxElement = document.getElementById(
      `box-${date.toISOString()}-${time}`
    );
    if (boxElement && selectionRect) {
      const boxRect = boxElement.getBoundingClientRect();
      const isOverlapping = !(
        boxRect.right < selectionRect.left ||
        boxRect.left > selectionRect.right ||
        boxRect.bottom < selectionRect.top ||
        boxRect.top > selectionRect.bottom
      );

      console.log("[BOX] Box Intersection Check", {
        boxId: `box-${date.toISOString()}-${time}`,
        isOverlapping,
        boxRect: {
          left: Math.round(boxRect.left),
          right: Math.round(boxRect.right),
          top: Math.round(boxRect.top),
          bottom: Math.round(boxRect.bottom),
        },
        selectionRect: {
          left: Math.round(selectionRect.left),
          right: Math.round(selectionRect.right),
          top: Math.round(selectionRect.top),
          bottom: Math.round(selectionRect.bottom),
        },
      });

      setIsBeingSelected(isOverlapping);

      if (!isOverlapping && !appendMode) {
        const dateTime = { date: date.toLocaleDateString("en-GB"), time };
        console.log("[DESELECT] Box Deselected", { dateTime });
        selectedElements.delete(dateTime);
        setSelectedElements(new CustomDateTimeSet(selectedElements));
      }

      if (isOverlapping) {
        const dateTime = { date: date.toLocaleDateString("en-GB"), time };
        console.log("[SELECT] Box Selected", { dateTime });
        selectedElements.add(dateTime);
        setSelectedElements(new CustomDateTimeSet(selectedElements));
      }
    } else {
      setIsBeingSelected(false);
    }
  }, [
    selectionRect,
    date,
    time,
    appendMode,
    selectedElements,
    setSelectedElements,
  ]);

  // Log selection state changes
  useEffect(() => {
    console.log("[STATE] Box State Update", {
      boxId: `box-${date.toISOString()}-${time}`,
      isSelected,
      isBeingSelected,
      appendMode,
    });
  }, [isSelected, isBeingSelected, date, time, appendMode]);

  // Enhanced visual feedback classes
  const baseClasses =
    "w-full h-8 rounded-md transition-all duration-150 border border-transparent";
  const selectedClasses = isSelected
    ? "bg-[rgba(200,80,80,0.8)] border-[rgba(200,80,80,0.9)] shadow-[inset_0_1px_4px_rgba(0,0,0,0.3)]"
    : "bg-dark-tertiary hover:bg-dark-secondary";
  const hoverClasses = "hover:border-[rgba(200,80,80,0.9)]";
  const activeClasses = isBeingSelected
    ? "scale-95 bg-[rgba(180,70,70,0.9)] border-[rgba(200,80,80,0.9)] shadow-[inset_0_2px_4px_rgba(0,0,0,0.4)]"
    : "";
  const touchFeedbackClasses =
    "active:scale-95 active:bg-[rgba(180,70,70,0.9)] active:shadow-[inset_0_2px_4px_rgba(0,0,0,0.4)]";

  return (
    <div
      id={`box-${date.toISOString()}-${time}`}
      data-testid="box"
      className={`
        ${baseClasses}
        ${selectedClasses}
        ${hoverClasses}
        ${activeClasses}
        ${touchFeedbackClasses}
      `}
      style={{
        touchAction: "none",
        WebkitTapHighlightColor: "transparent",
        cursor: "pointer",
      }}
    />
  );
}
