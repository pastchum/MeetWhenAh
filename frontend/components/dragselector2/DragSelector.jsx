'use client'
import { useRef, useState, useEffect } from 'react';

export default function DragSelector({ enabled, onSelectionChange }) {
    const [mouseDown, setMouseDown] = useState(false);
    const [startPoint, setStartPoint] = useState(null);
    const [endPoint, setEndPoint] = useState(null);
    const [selectionBox, setSelectionBox] = useState(null);
    const [selectedItems, setSelectedItems] = useState({});
    const [appendMode, setAppendMode] = useState(false);
    const [selectedChildren, setSelectedChildren] = useState({});
    
    const refs = useRef({});
    const mouseMoveHandler = useRef(null);
    const mouseUpHandler = useRef(null);
    useEffect(() => {
        if (mouseDown && selectionBox !== null) {
            updateCollidingChildren(selectionBox);
        }
    }, [mouseDown, selectionBox]);

    useEffect(() => {
        //cleanup if component unmounts
        return () => {
            if (mouseMoveHandler.current) {
                window.document.removeEventListener('mousemove', mouseMoveHandler.current);
            }
            if (mouseUpHandler.current) {
                window.document.removeEventListener('mouseUp', mouseUpHandler.current);
            }
        }
    }, [mouseDown])

    const onMouseDown = (e) => {
        if (!enabled || e.button === 2 || e.nativeEvent.button  === 2) return;
        if (e.ctrlKey || e.altKey || e.shiftKey ) {
            setAppendMode(true);
        }
        setMouseDown(true);
        setStartPoint({ x: e.pageX, y: e.pageY });


        //set event handlers
        mouseMoveHandler.current = onMouseMove;
        mouseUpHandler.current = onMouseUp;

        //add event listeners
        window.document.addEventListener('mousemove', mouseMoveHandler.current);
        window.document.addEventListener('mouseup', mouseUpHandler.current);
    };

    const onMouseMove = (e) => {

    }

    const onMouseUp = (e) => {
        window.document.removeEventListener('mousemove', mouseMoveHandler.current);
        window.document.removeEventListener('mouseUp', mouseUpHandler.current);
        setMouseDown(false);
        setStartPoint(null);
        setEndPoint(null);
        setSelectionBox(null);
        setAppendMode(false);
        
        onSelectionChange(Object.keys(selectedChildren.current));
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
        const newSelectedChildren = { ...selectedChildren }

        Object.keys(refs.current).forEach((key) => {
            if (key !== 'selectionBox') {
                const tmpNode = refs.current[key].current;
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
}