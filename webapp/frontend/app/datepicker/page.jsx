'use client'
import Image from "next/image";
import Details from '@/components/datepicker/Details'
import CustomDateRangePicker from '@/components/datepicker/CustomDateRangePicker'
import Summary from '@/components/datepicker/Summary'
import { useState, useEffect } from 'react'


export default function DatePicker() {
  const [data, setData] = useState({
    web_app_number: 0,
    event_name: "",
    event_details: "",
    start: "",
    end: "",
  })

  const [currentComponent, setCurrentComponent] = useState(0);

  const nextComponent = (newData) => {
    console.log("next component");
    setData({ ...data, ...newData});
    setCurrentComponent(currentComponent + 1);
  }

  const prevComponent = () => {
    console.log("prev component");
    setCurrentComponent(currentComponent - 1);
  }
  
  const [tg, setTg] = useState(null);
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
  
  return (
    <main className="dark-mode flex min-h-screen flex-col items-center justify-start overflow-hidden">
      <div className="pt-10">
        <p className="font-semibold text-gray-900 text-2xl"> MeetWhenAh? </p>
      </div>
      <div className="p-10">
            {currentComponent === 0 && <Details nextComponent={nextComponent} />}
            {currentComponent === 1 && <CustomDateRangePicker nextComponent={nextComponent} prevComponent={prevComponent} />}
            {currentComponent === 2 && <Summary prevComponent={prevComponent} nextComponent={submit} data={data} />}
      </div>
    </main>
  );
}
