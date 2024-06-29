'use client'
import Image from "next/image";
import Details from '@/components/datepicker/Details'
import CustomDateRangePicker from '@/components/datepicker/CustomDateRangePicker'
import Summary from '@/components/datepicker/Summary'
import { useState } from 'react'

export default function datePicker() {
  const [data, setData] = useState({
    event_name: "",
    event_details: "",
    startDate: "",
    endDate: "",
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


  return (
    <main className="dark-mode flex min-h-screen flex-col items-center justify-start">
      <div className="pt-10">
        <p className="font-semibold text-gray-900 text-2xl"> MeetWhenAh? </p>
      </div>
      <div className="p-10">
            {currentComponent === 0 && <Details nextComponent={nextComponent} />}
            {currentComponent === 1 && <CustomDateRangePicker nextComponent={nextComponent} prevComponent={prevComponent} />}
            {currentComponent === 2 && <Summary prevComponent={prevComponent} />}
      </div>
    </main>
  );
}
