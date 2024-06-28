import React, { useState, useEffect } from 'react'

const GridBox: React.FC = () => {
    


}

export default GridBox;


const Grid: React.FC = () => {
    let x = 7;
    let y = 48;

    const grid: React.ReactElement[] = [];
    for (let day = 0; day < x; day++) {
            for (let hour = 0; hour < y; hour++) {
                    grid.push(<GridBox />)
            }
    }
    return grid;


}