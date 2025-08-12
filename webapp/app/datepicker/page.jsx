"use client";
import EventForm from "@/components/datepicker/EventForm";
import EventDateSelector from "@/components/datepicker/EventDateSelector";
import ReviewSubmit from "@/components/datepicker/ReviewSubmit";
import { useState, useEffect } from "react";
import { useTelegramViewport } from "@/hooks/useTelegramViewport";
import { Card, CardBody, CardHeader } from "@nextui-org/react";

export default function DatePicker() {
  // Telegram viewport setup
  useTelegramViewport();

  const [data, setData] = useState({
    web_app_number: 0,
    event_name: "",
    event_details: "",
    start: null,
    end: null,
  });

  const [currentComponent, setCurrentComponent] = useState(0);

  const nextComponent = (newData) => {
    console.log("next component", newData);
    if (newData) {
      setData(prevData => ({ ...prevData, ...newData }));
      setCurrentComponent(prev => prev + 1);
    }
  };

  const prevComponent = () => {
    console.log("prev component");
    setCurrentComponent(prev => prev - 1);
  };

  const [tg, setTg] = useState(null);

  useEffect(() => {
    if (typeof window !== "undefined" && window.Telegram?.WebApp) {
      setTg(window.Telegram.WebApp);
    }
  }, []);

  useEffect(() => {
    if (tg) {
      try {
        tg.ready();
        tg.expand();
      } catch (error) {
        console.warn('Telegram WebApp error:', error);
      }
    }
  }, [tg]);

  return (
    <main className="minecraft-font bg-black min-h-screen flex flex-col items-center justify-start p-4">
      <div className="w-full max-w-md mb-6 text-center">
        <h1 className="font-semibold text-3xl">
          <span className="text-white">MeetWhen</span><span className="text-[#c44545]">?</span>
        </h1>
      </div>
      
      <div className="w-full max-w-md">
        {currentComponent === 0 && (
          <Card className="bg-[#0a0a0a] border border-white shadow-lg">
            <CardBody className="p-6">
              <EventForm nextComponent={nextComponent} initialData={data} />
            </CardBody>
          </Card>
        )}
        {currentComponent === 1 && (
          <Card className="bg-[#0a0a0a] border border-white shadow-lg">
            <CardBody className="p-6">
              <EventDateSelector
                nextComponent={nextComponent}
                prevComponent={prevComponent}
                initialData={data}
              />
            </CardBody>
          </Card>
        )}
        {currentComponent === 2 && (
          <Card className="bg-[#0a0a0a] border border-white shadow-lg">
            <CardBody className="p-6">
              <ReviewSubmit data={data} prevComponent={prevComponent} />
            </CardBody>
          </Card>
        )}
      </div>
    </main>
  );
}
