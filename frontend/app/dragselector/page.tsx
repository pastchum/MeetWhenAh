'use client'
import { useEffect, useRef, useContext, createContext, forwardRef, ReactNode, useState } from 'react';
import DragSelector from '@/components/dragselector/DragSelector'
import CustomDateTimeSet from '@/components/dragselector/CustomDateTimeSet';


export default function Home() {  

  const [tg, setTg] = useState<any>(null);
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

  const [data, setData] = useState({
    web_app_number: 1,
    event_name: "",
    event_id:"",
    start: new Date(),
    end: new Date(),
  })

  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    setData((oldData:any):any => {
      const start = params.get('start');
      const end = params.get('end');
      const event_name = params.get("event_name");
      const event_id = params.get("event_id");
      if (start && end && event_id && event_name){
        return {
          ...oldData,
          start: new Date(start),
          end: new Date(end),
          event_name: event_name,
          event_id: event_id
        }
      }
      
    })
  }, [])

  console.log(data)
  const [selectedElements, setSelectedElements] = useState<CustomDateTimeSet>(new CustomDateTimeSet());
  const [removeNight, setRemoveNight] = useState<boolean>(true);

  const d = new Date("2022-03-25");
  return (
    <main className="dark-mode bg-zinc-200 h-screen">
      <p className="text-3xl font-bold text-center pt-1"> Select Timings </p>
      <p className="text-2sm font-bold text-center"> {data.start} </p>
      <DragSelector removeNight={removeNight} startDate={d} numDays={7} selectedElements={selectedElements} setSelectedElements={setSelectedElements} />
    </main>
  );
}
