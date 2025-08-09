import { useState } from 'react';
import NextButton from "@/components/datepicker/NextButton";

export default function EventForm({ initialData, nextComponent }) {
    const [data, setData] = useState(initialData || { event_name: "", event_details: "" });

    const handleChange = (field, value) => {
        setData(prev => ({
            ...prev,
            [field]: value
        }));
    };

    return (
        <div className="relative w-full max-w-md mx-auto">
            <div className="mb-20 minecraft-font" data-testid="details">
                <div className="space-y-8 px-4 py-6">
                    <div>
                        <label htmlFor="eventName" className="block text-sm font-medium leading-6 text-[#c44545] minecraft-font mb-2">
                            Event Name
                        </label>
                        <input
                            type="text"
                            name="eventName"
                            id="eventName"
                            value={data.event_name || ""}
                            onChange={(e) => handleChange('event_name', e.target.value)}
                            className="block w-full rounded-md border-2 border-white bg-[#1a1a1a] py-3 px-4 text-white shadow-sm placeholder:text-[#a0a0a0] focus:ring-[#c44545] focus:border-[#c44545] focus:outline-none sm:text-sm sm:leading-6 text-center minecraft-font"
                            placeholder="Enter event name"
                        />
                    </div>

                    <div>
                        <label htmlFor="eventDetails" className="block text-sm font-medium leading-6 text-[#c44545] minecraft-font mb-2">
                            Event Details
                        </label>
                        <textarea
                            name="eventDetails"
                            id="eventDetails"
                            rows={6}
                            value={data.event_details || ""}
                            onChange={(e) => handleChange('event_details', e.target.value)}
                            className="block w-full rounded-md border-2 border-white bg-[#1a1a1a] py-3 px-4 text-white shadow-sm placeholder:text-[#a0a0a0] focus:ring-[#c44545] focus:border-[#c44545] focus:outline-none sm:text-sm sm:leading-6 minecraft-font resize-none"
                            placeholder="Describe your event"
                        />
                    </div>
                </div>
            </div>

            <div className="absolute bottom-0 right-0">
                <NextButton
                    disabled={!data.event_name?.trim()}
                    onClick={() => nextComponent(data)}
                    newData={data}
                />
            </div>
        </div>
    );
}