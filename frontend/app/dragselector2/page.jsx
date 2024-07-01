'use client'
import DragSelector from '@/components/dragselector2/DragSelector'
import DragBox from '@/components/dragselector2/DragBox'
import React from 'react';
import './style.css'

export default function DragSelector2() {
    

    const handleSelectionChange = (selectedKeys) => {
        console.log('Selected items:', selectedKeys);
    };

    var data = [];
    for(var i = 0; i < 65; i++) {
    data.push(
        <DragBox data={i} key={i} />
    );
    }

    return (
        <div>
            <div id ="example">
            <DragSelector enabled={true} onSelectionChange={handleSelectionChange}>
                {data}
            </DragSelector>
            </div>
            
        </div>
        
    )
}