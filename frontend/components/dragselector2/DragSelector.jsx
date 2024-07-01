'use client'
import React, { useRef, useState, useEffect, forwardRef} from 'react';

export default function DragSelector({ enabled, onSelectionChange, children }) {
    const [mouseDown, setMouseDown] = useState(false);
    const [startPoint, setStartPoint] = useState(null);
    const [endPoint, setEndPoint] = useState(null);
    const [selectionBox, setSelectionBox] = useState(null);
    const [selectedItems, setSelectedItems] = useState({});
    const [appendMode, setAppendMode] = useState(false);
    const [selectedChildren, setSelectedChildren] = useState({});
    
    let refs = useRef({});
    let selectionBoxRef = useRef();
    const mouseMoveHandler = useRef(null);
    const mouseUpHandler = useRef(null);

    useEffect(() => {
        if (mouseDown && selectionBox !== null) {
            updateCollidingChildren(selectionBox);
        }
    }, [mouseDown, selectionBox]);

    // useEffect(() => {
    //     //cleanup if component unmounts
    //     return () => {
    //         if (mouseMoveHandler.current) {
    //             window.document.removeEventListener('mousemove', mouseMoveHandler.current);
    //         }
    //         if (mouseUpHandler.current) {
    //             window.document.removeEventListener('mouseUp', mouseUpHandler.current);
    //         }
    //     }
    // })



    const onMouseMove = (e) => {
        console.log("moving")
        //console.log(mouseDown);
        
        e.preventDefault();
        if (mouseDown) {
            console.log("mouse is down")
            var endPoint = {
                x: e.pageX,
                y: e.pageY
            };
            setEndPoint(endPoint);
            setSelectionBox(calculateSelectionBox(startPoint, endPoint))
            
        }
    }

    // useEffect(() => {
    //     console.log("SELECTIONBOX")
    //     console.log(selectionBox)
    // },[selectionBox]);

    const onMouseUp = (e) => {
        
        window.document.removeEventListener('mousemove', mouseMoveHandler.current);
        window.document.removeEventListener('mouseup', mouseUpHandler.current);
        
        setStartPoint(null);
        setEndPoint(null);
        setSelectionBox(null);
        setAppendMode(false);
        console.log("mouseup")
        setMouseDown(false);
        onSelectionChange(Object.keys(selectedChildren));
    }


    useEffect(() => {
        //set event handlers
        mouseMoveHandler.current = onMouseMove;
        mouseUpHandler.current = onMouseUp;

        if (mouseDown) {
            //add event listeners
            window.document.addEventListener('mousemove', mouseMoveHandler.current);
            window.document.addEventListener('mouseup', mouseUpHandler.current);
        }
        else{
            window.document.removeEventListener('mousemove', mouseMoveHandler.current);
            window.document.removeEventListener('mouseup', mouseUpHandler.current);
        }
        
    }, [mouseDown]);

    const onMouseDown = (e) => {
        if (!enabled || e.button === 2 || e.nativeEvent.button  === 2) return;
        if (e.ctrlKey || e.altKey || e.shiftKey ) {
            setAppendMode(true);
        }
        console.log(mouseDown);
        setMouseDown(true);
        console.log(mouseDown);
        setStartPoint({ x: e.pageX, y: e.pageY });
        //console.log("mouseDOWN HERE")
        
        
    };

    
    
    const selectItem = (key, isSelected) => {
        console.log("selecting...")
        if (isSelected) {
            selectedChildren[key] = isSelected;
        }
        else {
            delete selectedChildren[key];
        }
        //console.log(Object.keys(selectedChildren))
        onSelectionChange(Object.keys(selectedChildren));
        

        // setSelectedChildren((prevSelectedChildren) => {
        //     const newSelectedChildren = {...prevSelectedChildren};
        //     if (isSelected) {
        //         newSelectedChildren[key] = isSelected;
        //     }
        //     else {
        //         delete newSelectedChildren[key];
        //     }
        //     console.log(Object.keys(newSelectedChildren));
        //     onSelectionChange(Object.keys(newSelectedChildren));
        //     return newSelectedChildren;
        // })
    }

    const calculateSelectionBox = (startPoint, endPoint) => {
        //console.log("here");
        if (!mouseDown || endPoint === null || startPoint === null) return null;
        //console.log("calculating");
        let parentNode = selectionBoxRef.current;
        //console.log(parentNode);
        let left = Math.min(startPoint.x, endPoint.x) - parentNode.offsetLeft;
        let top = Math.min(startPoint.y, endPoint.y) - parentNode.offsetTop;
        let width = Math.abs(startPoint.x - endPoint.x);
        let height = Math.abs(startPoint.y - endPoint.y);
        console.log({
            left: left,
            top: top,
            width: width,
            height: height
        })
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
        console.log("colliding...");
        const newSelectedChildren = { ...selectedChildren }

        console.log(selectionBoxRef.current)
        Object.keys(selectionBoxRef.current).forEach((key) => {
            if (key !== 'selectionBoxRef') {
                const tmpNode = selectionBoxRef.current[key];
                console.log(key)
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
            const tmpRef = useRef(tmpKey);
            const clonedChild = React.cloneElement(child, {
                ref: tmpRef,
                isSelected: isSelected
            })
            //console.log(clonedChild)
            return (
                <div className={`select-box ${isSelected ? 'selected' : ''}`}
                    onClickCapture={(e) => {
                        if ((e.ctrlKey || e.altKey || e.shiftKey)) {
                        e.preventDefault();
                        e.stopPropagation();
                        selectItem(tmpKey, !isSelected);
                        }
                    }}
                >
                    { clonedChild }
                </div>
            );
        });
    }

    const renderSelectionBox = () => {
        if (!mouseDown || !endPoint || !startPoint) return null;
        return (
            <div className='selection-border' style={selectionBox}></div>
        )
    }

    //console.log(selectionBox);
    return (
        <div
            className={`absolute selection ${mouseDown ? 'dragging' : ''}`} // you set absolute here to get your calculateSelectionBox right
            ref={selectionBoxRef}
            onMouseDown={onMouseDown}
        >
        
        { renderChildren({children}) }
        { renderSelectionBox() }
        </div>
    )   

}