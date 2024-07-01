import {forwardRef} from 'react';
export const DragBox = forwardRef(({ isSelected, data}, ref) =>{
    //console.log({data})
    let className='item noselect';
    className += isSelected ? ' selected' : '';
    return (
        <div className={className} ref={ref}>
            Item {data + 1}
        </div>
    );
})

export default DragBox;