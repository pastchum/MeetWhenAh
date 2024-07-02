'use client'
import React, { useRef, useState, useEffect} from 'react';

export default function DragSelector({ enabled, onSelectionChange, children }) {
    const [mouseDown, setMouseDown] = useState(false);
    const [touchStart, setTouchStart] = useState(false);
    const [startPoint, setStartPoint] = useState(null);
    const [endPoint, setEndPoint] = useState(null);
    const [selectionBox, setSelectionBox] = useState(null);
    const [appendMode, setAppendMode] = useState(false);
    const [selectedChildren, setSelectedChildren] = useState({});
    
    const childRefs = useRef({});
    const selectionBoxRef = useRef();
    const touchMoveHandler = useRef(null);
    const touchEndHandler = useRef(null);
    const mouseMoveHandler = useRef(null);
    const mouseUpHandler = useRef(null);

    useEffect(() => {
        if (mouseDown && selectionBox !== null) {
            updateCollidingChildren(selectionBox);
        }
        if (touchStart && selectionBox !== null) {
            updateCollidingChildren(selectionBox);
        }
    }, [touchStart, mouseDown, selectionBox]);


    const getSelectedSubNode = (child) => {
        return child.children[0];
    }


    const onTouchMove = (e) => {
        if (touchStart) {
            var endPoint = {
                x: e.touches[0].pageX,
                y: e.touches[0].pageY
            };
            setEndPoint(endPoint);
            setSelectionBox(calculateSelectionBox(startPoint, endPoint))
        }
    }

    const onMouseMove = (e) => {
        e.preventDefault();
        if (mouseDown) {
            var endPoint = {
                x: e.pageX,
                y: e.pageY
            };
            setEndPoint(endPoint);
            
            
            setSelectionBox(calculateSelectionBox(startPoint, endPoint))
            
        }
    }

    const onTouchEnd = (e) => {
        window.document.removeEventListener('touchmove', touchMoveHandler.current);
        window.document.removeEventListener('touchend', touchEndHandler.current);
        
        setStartPoint(null);
        setEndPoint(null);
        setSelectionBox(null);
        setTouchStart(false);
        
        
        let subChildElements = []
        for (const key in selectedChildren) subChildElements.push(getSelectedSubNode(childRefs.current[key]))
        onSelectionChange(subChildElements);
    }

    const onMouseUp = (e) => {
        window.document.removeEventListener('mousemove', mouseMoveHandler.current);
        window.document.removeEventListener('mouseup', mouseUpHandler.current);
        
        setStartPoint(null);
        setEndPoint(null);
        setSelectionBox(null);
        setAppendMode(false);
        setMouseDown(false);

        let subChildElements = []
        for (const key in selectedChildren) subChildElements.push(getSelectedSubNode(childRefs.current[key]))
        onSelectionChange(subChildElements);
    }


    useEffect(() => {
        //set event handlers
        mouseMoveHandler.current = onMouseMove;
        mouseUpHandler.current = onMouseUp;
        touchMoveHandler.current = onTouchMove;
        touchEndHandler.current = onTouchEnd;

        if (touchStart) {
            window.document.addEventListener('touchmove', touchMoveHandler.current);
            window.document.addEventListener('touchend', touchEndHandler.current);
        }
        else if (mouseDown) {
            //add event listeners
            window.document.addEventListener('mousemove', mouseMoveHandler.current);
            window.document.addEventListener('mouseup', mouseUpHandler.current);
        }
        else{
            window.document.removeEventListener('mousemove', mouseMoveHandler.current);
            window.document.removeEventListener('mouseup', mouseUpHandler.current);

            window.document.removeEventListener('touchmove', touchMoveHandler.current);
            window.document.removeEventListener('touchend', touchEndHandler.current);
        }
        
    }, [touchStart, mouseDown]);

    const onMouseDown = (e) => {
        if (!enabled || e.button === 2 || e.nativeEvent.button  === 2) return;
        if (e.ctrlKey || e.altKey || e.shiftKey ) {
            setAppendMode(true);
        }

        setMouseDown(true);
        setStartPoint({ x: e.pageX, y: e.pageY });
        
    };

    const onTouchStart = (e) => {
        setAppendMode(true);
        setTouchStart(true);
        setStartPoint({ x: e.touches[0].pageX, y: e.touches[0].pageY });
    };

    
    
    const selectItem = (key, isSelected) => {
        let newSelectedChildren = {...selectedChildren};
        if (isSelected) {
            newSelectedChildren[key] = isSelected;
        }
        else {
            delete newSelectedChildren[key];
        }

        setSelectedChildren({...newSelectedChildren})
        

        let subChildElements = []
        for (const key in selectedChildren) subChildElements.push(getSelectedSubNode(childRefs.current[key]))
        onSelectionChange(subChildElements);
        
        
    }

    const calculateSelectionBox = (startPoint, endPoint) => {
        if (!(!mouseDown || !touchStart) || endPoint === null || startPoint === null) return null;
        let parentNode = selectionBoxRef.current;
        let left = Math.min(startPoint.x, endPoint.x) - parentNode.offsetLeft;
        let top = Math.min(startPoint.y, endPoint.y) - parentNode.offsetTop;
        let width = Math.abs(startPoint.x - endPoint.x);
        let height = Math.abs(startPoint.y - endPoint.y);
        return {
            left: left,
            top: top,
            width: width,
            height: height
        };
    }



    const boxIntersects = (boxA, boxB) => {
        if(boxA.left <= boxB.left + boxB.width &&
            boxA.left + boxA.width >= boxB.left &&
            boxA.top <= boxB.top + boxB.height &&
            boxA.top + boxA.height >= boxB.top) 
            {
                return true;
            }
        return false;
    }

    const updateCollidingChildren = (selectionBox) => {
        let newSelectedChildren = { ...selectedChildren }
        Object.keys(childRefs.current).forEach((key) => {
            if (key !== 'selectionBoxRef') {
                const tmpNode = childRefs.current[key];
                const tmpBox = {
                    top: tmpNode.offsetTop,
                    left: tmpNode.offsetLeft,
                    width: tmpNode.clientWidth,
                    height: tmpNode.clientHeight
                };
                if (boxIntersects(selectionBox, tmpBox)){
                    newSelectedChildren[key] = true;
                }
                else {
                    if (!appendMode) {
                        delete newSelectedChildren[key];
                    }
                }
            }
        }) 
        setSelectedChildren(newSelectedChildren);
    }

    const renderChildren = ({ children }) => {
        let index = 0;
        return React.Children.map(children, (child) => {
            if (!child) return null;
            
            const tmpKey = child.key === null ? index++ : child.key;
            let isSelected = selectedChildren.hasOwnProperty(tmpKey);
            const clonedChild = React.cloneElement(child, {
                isSelected: isSelected
            })
            return (
                <div className={`select-box ${isSelected ? 'selected bg-zinc-400' : ''} w-96px h-100px text-xs m-2   `}
                    onClick={(e) => {
                        if ((e.ctrlKey || e.altKey || e.shiftKey)) { 
                            e.preventDefault();
                            e.stopPropagation();
                            selectItem(tmpKey, !isSelected);
                        }  
                    }}
                    ref={(el) => childRefs.current[tmpKey] = el}
                >
                    { clonedChild }
                </div>
            );
        });
    }

    const renderSelectionBox = () => {
        if (!(mouseDown || touchStart) || !endPoint || !startPoint) {  
            return null;
        }
        return (
            <div className='absolute selection-border bg-slate-100 z-index: 99 bg-opacity-60 ' style={selectionBox}></div>
        )
    }

    return (
        <div
            className={`text-black grid grid-flow-col grid-rows-48 grid-cols-12 absolute selection ${mouseDown ? 'dragging' : ''}`} // you set absolute here to get your calculateSelectionBox right
            ref={selectionBoxRef}
            onMouseDown={onMouseDown}
            onTouchStart={onTouchStart}
        >
        
        { renderChildren({children}) }
        { renderSelectionBox() }
        </div>
    )   

}