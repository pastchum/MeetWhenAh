// components/DragSelect.tsx
'use client'

import React, { useState, useRef, useEffect } from 'react';

interface Box {
  top: number;
  left: number;
  width: number;
  height: number;
}

const DragSelect: React.FC = () => {
  const [isDragging, setIsDragging] = useState(false);
  const [box, setBox] = useState<Box | null>(null);
  const startPos = useRef<{ x: number; y: number }>({ x: 0, y: 0 });

  const handleMouseDown = (e: React.MouseEvent) => {
    startPos.current = { x: e.clientX, y: e.clientY };
    setIsDragging(true);
    setBox({ top: e.clientY, left: e.clientX, width: 0, height: 0 });
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isDragging) return;

    const currentPos = { x: e.clientX, y: e.clientY };
    const newBox = {
      top: Math.min(startPos.current.y, currentPos.y),
      left: Math.min(startPos.current.x, currentPos.x),
      width: Math.abs(currentPos.x - startPos.current.x),
      height: Math.abs(currentPos.y - startPos.current.y),
    };
    setBox(newBox);
  };

  const handleMouseUp = () => {
    setIsDragging(false);
    // Handle completed drag action here
  };

  return (
    <div
      onMouseDown={handleMouseDown}
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      onMouseLeave={() => setIsDragging(false)}
      style={{ position: 'relative', width: '100%', height: '100vh', userSelect: 'none' }}
    >
      {box && (
        <div
          style={{
            position: 'absolute',
            top: box.top,
            left: box.left,
            width: box.width,
            height: box.height,
            backgroundColor: 'rgba(0, 120, 215, 0.3)',
            border: '1px solid rgba(0, 120, 215, 0.8)',
          }}
        />
      )}
    </div>
  );
};

export default DragSelect;