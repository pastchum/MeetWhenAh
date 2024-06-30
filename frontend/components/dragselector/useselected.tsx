// components/DragSelect.tsx

import React, { useState, useRef, useEffect } from 'react';

export default function useSelected(
  elementRef: React.RefObject<HTMLElement>,
  selection: DOMRect | null
) {
  const [isSelected, setIsSelected] = React.useState<Boolean>(false);

  React.useEffect(() => {
    if (!elementRef.current || !selection) {
      setIsSelected(false);
    } else {
      console.log(".");
      const a = elementRef.current.getBoundingClientRect();
      const b = selection;
      setIsSelected(
        !(
          a.y + a.height < b.y ||
          a.y > b.y + b.height ||
          a.x + a.width < b.x ||
          a.x > b.x + b.width
        )
      );
    }
  }, [elementRef, selection]);

  return isSelected;
}


