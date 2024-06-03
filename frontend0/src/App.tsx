import { useState, useEffect } from 'react'
import reactLogo from './assets/react.svg'
import './App.css'
import { Theme, Flex, Text} from '@radix-ui/themes';
import { Button, } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import EventInput from './elements/EventInput';
import { Calendar } from "@/components/ui/calendar"
import { ThemeProvider } from "@/components/theme-provider"
// import { BrowserRouter as Router, Route, Routes, BrowserRouter } from 'react-router-dom';
import { string } from 'zod';
import DateRangePicker from './elements/DateRangePicker';
import { ModeToggle } from './components/mode-toggle';
import EventMessage from './elements/EventMessage';
import Navbar from './NavBar';
import { Routes, Route} from "react-router-dom";
import { DateRange } from 'react-day-picker';
import { format } from 'date-fns';
 

type EventData = {
  eventName: string;
  eventDetails: string;
};
declare global {
  interface Window {
    Telegram: any; // Use `any` or a more specific type if available
  }
}

function App(): JSX.Element{
  const [tg, setTg] = useState<any>(null);
  const [eventName, setEventName] = useState<string>('');
  const [eventDetails, setEventDetails] = useState<string>('');
  const [startDate, setStartDate] = useState<Date | null>(null);
  const [endDate, setEndDate] = useState<Date | null>(null);  
  useEffect(() => {
    if (window.Telegram) {
      setTg(window.Telegram.WebApp);
      // Now you can use the Telegram Web App API
      // For example, getting the user data:
      
    } else {
      console.error("Telegram Web App script not loaded");
    }
  }, []);
  const handleEventData = (eventName: string, eventDetails: string) => {
    setEventName(eventName);
    setEventDetails(eventDetails);
    // Handle the event data here
    console.log('Event Name:', eventName);
    console.log('Event Details:', eventDetails);
  };
  const handleDateRange = (data : DateRange) => {
    if (data.from && data.to) {
      setStartDate(data.from);
      setEndDate(data.to);
    }
    console.log(startDate)
    console.log(endDate)
  }
  type ComponentType = 'A' | 'B' | 'C';
  const [activeComponent, setActiveComponent] = useState<ComponentType>('A');
  const showComponent = (component: ComponentType) => {
    setActiveComponent(component);
  };
  const handleEventMessage = () => {
    const preJsonData = {
      web_app_number: 0,
      event_name: eventName,
      event_details: eventDetails,
      start_date: startDate ? format(startDate, 'dd-MM-yyyy') : null,
      end_date: endDate ? format(endDate, 'dd-MM-yyyy') : null
    }
    const jsonData = JSON.stringify(preJsonData, null, 4)
    console.log(eventName);
    console.log(eventDetails);
    console.log(jsonData);
    tg.sendData(jsonData)
  }
  
  const handleExit = () => {
    tg.close();
  }

  return (
    <ThemeProvider defaultTheme= "dark" storageKey="vite-ui-theme">
      <h3 className="absolute top-0 left-0 text-2xl p-4 font-semibold tracking-tight">meet when ah?</h3>
      {activeComponent === 'A' && <EventInput handleEventData = {handleEventData} handleCreateEvent= {() => showComponent('B')}></EventInput>}
      {activeComponent === 'B' && <DateRangePicker handleDateRange = {handleDateRange} handleBackToEventDetails = { ()=> showComponent('A')} handleNextTab = { () => showComponent('C')}></DateRangePicker>}
      {activeComponent === 'C' && <EventMessage handleEventMessage = {handleEventMessage} handleEdit = { ()=> showComponent('B')} handleExit = {handleExit}></EventMessage> }
      </ThemeProvider>
  )
}
export default App
