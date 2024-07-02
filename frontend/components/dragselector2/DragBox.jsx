import {forwardRef} from 'react';
export const DragBox = ({isSelected, data}) => {
    //console.log({data})
    let className='item noselect ';
    className += isSelected ? ' selected' : '';
    return (
        <div className={className}>
            {data}
        </div>
    );
}

export default DragBox;