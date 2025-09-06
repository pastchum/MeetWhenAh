// components/DragSelect.tsx

import { useState, useRef, useEffect } from "react";
import CustomDateTimeSet from "@/components/dragselector/CustomDateTimeSet";
import { DateTime } from "./CustomDateTimeSet";

function isWithinSelectionBox(a: DOMRect, b: DOMRect) {
  return !(
    a.y + a.height < b.y ||
    a.y > b.y + b.height ||
    a.x + a.width < b.x ||
    a.x > b.x + b.width
  );
}

export default function UseSelected(
  elementRef: React.RefObject<HTMLElement>,
  selection: DOMRect | null,
  isAlreadySelected: boolean,
  appendMode: boolean
) {
  const [isSelected, setIsSelected] = useState<Boolean>(false);

  useEffect(() => {
    if (!elementRef.current || !selection) {
      //setIsSelected(false);
    } else {
      const a = elementRef.current.getBoundingClientRect();
      const b = selection;
      if (appendMode) {
        setIsSelected(isWithinSelectionBox(a, b) || isAlreadySelected);
      } else {
        setIsSelected(isWithinSelectionBox(a, b));
      }
    }
  }, [elementRef, selection, isSelected, isAlreadySelected, appendMode]);

  return isSelected;
}
