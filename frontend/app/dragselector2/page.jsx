'use client'
import DragSelector from '@/components/dragselector2/DragSelector'
import DragBox from '@/components/dragselector2/DragBox'
import React from 'react';
import { useState, useEffect } from 'react';
import './style.css'
import Toggle from "@/components/dragselector2/Toggle";

function getQueryParams() {
    const params = {};
    const queryString = window.location.search;
    const urlParams = new URLSearchParams(queryString);
  
    urlParams.forEach((value, key) => {
      params[key] = value;
    });
  
    return params;
  }

  


export default function DragSelector2() {
    const [tg, setTg] = useState(null);

    const [stateData, setStateData] = useState({
        web_app_number: 1,
        event_name: "",
        event_id: "",
        start: "",
        end: "",
    });
    
    useEffect(() => {
        // Parse query parameters when the component mounts
        const queryParams = getQueryParams();
        queryParams['start'] = new Date(queryParams['start'])
        queryParams['end'] = new Date(queryParams['end'])

        // Update state with query parameters
        setStateData(prevData => ({
          ...prevData,
          ...queryParams
        }));
        
        

      }, []); 

    useEffect(() => {
        if (window.Telegram) {
        setTg(window.Telegram.WebApp);
        } else {
        console.error("Telegram Web App script not loaded");
        }
    }, []);

    const submit = () => {
        data.start = data.start.toString();
        data.end = data.end.toString();
        console.log(data);
        tg.sendData(JSON.stringify(data, null, 4));
        tg.close()
        }

    const handleSelectionChange = (nodes) => {
        for (const node of nodes) console.log(node.dataset.day);
        
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
        for (let i = -48; i < totalHalfHours; i++) {
            const day = Math.floor(i / 48) ;
            const time = formatTime(i % 48);
            if (time == "0000") {
                data.push(
                    <DragBox data={`Day ${day}, Time -0100`} key={-1} />
                );
            }
            data.push(
                <DragBox data={`Day ${day}, Time ${time}`} key={i} />
            );
        }

        //console.log(data);

        return data;
    }
    const dayDiff = (stateData['end'] - stateData['start']) / (1000 * 60 * 60 * 24);
    const pages = dayDiff/7;
    //console.log(stateData);
    return (
        <div className="dark-mode bg-grey-400 text-center w-screen overflow-hidden">
            <div>
                <Toggle />
            </div>
            <div className="overflow-hidden items-center justify-between ">
                <div className="">
                    <DragSelector enabled={true} onSelectionChange={handleSelectionChange}>
                        {DayGrid(7)}
                    </DragSelector>
                </div>
                
            </div>
        </div>
        
        
    )
}