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
    }
    const handleDetailsChange = (e) => {
        setNewData({...newData, event_details: e.target.value});
    }
    
    return (
        <div className="relative space-y-5 sm:space-y-14 w-[80vw] sm:w-[60vw] pb-10"
             data-testid="details">
            <Name handleInputChange={handleNameChange} />
            <TextArea handleInputChange={handleDetailsChange} />
            <div className="absolute right-0">
                <NextButton disabled={!newData.event_name} onClick={nextComponent} newData={newData} />
            </div>
        </div>    
    )
}