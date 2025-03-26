"use client";

import Image from "next/image";
import { useState } from "react";
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";

export default function Home() {
  const [eventName, setEventName] = useState('');
  const [eventDetails, setEventDetails] = useState('');
  const [startDate, setStartDate] = useState<Date | null>(null);
  const [endDate, setEndDate] = useState<Date | null>(null);
  const [eventType, setEventType] = useState('general');
  const [autoJoin, setAutoJoin] = useState(true);

  const handleSubmit = () => {
    if (!eventName || !startDate || !endDate) {
      alert('Please fill in all required fields');
      return;
    }

    const data = {
      web_app_number: 0,
      event_name: eventName,
      event_details: eventDetails,
      start: startDate.toISOString().split('T')[0],
      end: endDate.toISOString().split('T')[0],
      event_type: eventType,
      auto_join: autoJoin
    };

    if (window.Telegram?.WebApp) {
      window.Telegram.WebApp.sendData(JSON.stringify(data));
      window.Telegram.WebApp.close();
    }
  };

  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24">
      <h1>You&apos;re not supposed to be here!</h1>

      <div className="flex flex-col space-y-4 p-4">
        <h1 className="text-2xl font-bold mb-4">Create New Event</h1>
        
        <div className="space-y-2">
          <label className="block text-sm font-medium">Event Name</label>
          <input
            type="text"
            value={eventName}
            onChange={(e) => setEventName(e.target.value)}
            className="w-full p-2 border rounded"
            placeholder="Enter event name"
          />
        </div>

        <div className="space-y-2">
          <label className="block text-sm font-medium">Event Details</label>
          <textarea
            value={eventDetails}
            onChange={(e) => setEventDetails(e.target.value)}
            className="w-full p-2 border rounded"
            placeholder="Add event details (optional)"
          />
        </div>

        <div className="space-y-2">
          <label className="block text-sm font-medium">Event Type</label>
          <select
            value={eventType}
            onChange={(e) => setEventType(e.target.value)}
            className="w-full p-2 border rounded"
          >
            <option value="general">General</option>
            <option value="work">Work</option>
            <option value="social">Social</option>
            <option value="study">Study</option>
          </select>
        </div>

        <div className="space-y-2">
          <label className="block text-sm font-medium">Start Date</label>
          <DatePicker
            selected={startDate}
            onChange={(date: Date | null) => setStartDate(date)}
            className="w-full p-2 border rounded"
            placeholderText="Select start date"
          />
        </div>

        <div className="space-y-2">
          <label className="block text-sm font-medium">End Date</label>
          <DatePicker
            selected={endDate}
            onChange={(date: Date | null) => setEndDate(date)}
            className="w-full p-2 border rounded"
            placeholderText="Select end date"
          />
        </div>

        <div className="flex items-center space-x-2">
          <input
            type="checkbox"
            checked={autoJoin}
            onChange={(e) => setAutoJoin(e.target.checked)}
            className="rounded border-gray-300"
            id="autoJoin"
          />
          <label htmlFor="autoJoin" className="text-sm font-medium">
            Automatically join this event
          </label>
        </div>

        <button
          onClick={handleSubmit}
          className="w-full bg-blue-500 text-white p-2 rounded hover:bg-blue-600"
        >
          Create Event
        </button>
      </div>
    </main>
  );
}
