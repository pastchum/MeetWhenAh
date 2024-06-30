import Name from '@/components/datepicker/Details/Name'
import TextArea from '@/components/datepicker/Details/TextArea'
import NextButton from '@/components/datepicker/NextButton'
import { useState } from 'react';
export default function Details({ nextComponent }) {

    const [newData, setNewData] = useState({
        event_name: "",
        event_details: ""
    })

    const handleNameChange = (e) => {
        setNewData({...newData, event_name: e.target.value});
        //console.log(newData);
    }
    const handleDetailsChange = (e) => {
        setNewData({...newData, event_details: e.target.value});
        //console.log(newData);
    }
    

    return (
        <div className="relative space-y-14 w-[80vw] sm:w-[60vw]">
            <Name handleInputChange={handleNameChange}/>
            <TextArea handleInputChange={handleDetailsChange} />
            <div className="absolute right-0">
                <NextButton onClick={nextComponent} newData={newData} />
            </div>
        </div>    
    )
}