import {forwardRef} from 'react';
export const DragBox = ({isSelected, data}) => {
    //console.log({data})
    let className='item noselect ';
    const parts = data.split(",").map(part => part.trim());
    // Extract the day and time parts
    const dayPart = parts[0];
    const timePart = parts[1];

    // Extract the integer values from the strings
    const day = parseInt(dayPart.replace('Day ', ''), 10);
    const time = parseInt(timePart.replace('Time ', ''), 10);

    if (data.includes("-")) {
        var newData = ""
        
        if (day < 0) {
            newData = time + 2400;
            if (newData % 100 != 0) {
                newData = newData + 60
            }
        }
        else if (time < 0){
            newData = day;
        }

        return (
            <div className={`${className} bg-gray-200 border border-gray-400 rounded-lg p-1 select-none data-day=${day} data-time=${time}`} >
                {newData}
            </div>
        )
    }
    else{
        className += isSelected ? ' selected' : '';
        return (
            <div id="inner" className={`${className} bg-gray-200 border border-gray-400 rounded-lg p-1 select-none data-day=${day} data-time=${time}`} >
                {/* {data} */}
            </div>
        );
    }
    
}

export default DragBox;