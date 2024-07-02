'use client'
import DragSelector from '@/components/dragselector2/DragSelector'
import DragBox from '@/components/dragselector2/DragBox'
import React from 'react';
import './style.css'

export default function DragSelector2() {
    

    const handleSelectionChange = (nodes) => {
        for (const node of nodes) console.log('Selected items: ' + node.innerText);
        
    };

    const DayGrid = (numDays) => {
        // Generate an array with the total number of DragBoxes needed
        const totalHalfHours = numDays * 48;  // 48 half-hours per day
      
        const formatTime = (halfHourIndex) => {
            const hour = Math.floor(halfHourIndex / 2);
            const minutes = halfHourIndex % 2 === 0 ? '00' : '30';
            return `${hour.toString().padStart(2, '0')}${minutes}`;
          };
      
        // Generate the DragBox components
        const data = [];
        for (let i = 0; i < totalHalfHours; i++) {
            const day = Math.floor(i / 48) + 1;
            const time = formatTime(i % 48);
            data.push(
                <DragBox data={`Day ${day}, Time ${time}`} key={i} />
            );
        }

        //console.log(data);
        return data;
    }

    return (
        <div className="overflow-hidden">
            <div id="example" className="">
                <DragSelector enabled={true} onSelectionChange={handleSelectionChange}>
                    {DayGrid(10)}
                </DragSelector>
                
            </div>
            
        </div>
        
    )
}