import { useState, useEffect } from "react";
import DatePicker from "react-datepicker";
import { CalendarDaysIcon, ClockIcon } from "@heroicons/react/24/outline";
import "react-datepicker/dist/react-datepicker.css";

interface ConfirmDatePickerProps {
  startDate?: any;
  endDate?: any;
  onDateChange?: (dates: {
    startDate: Date | null;
    endDate: Date | null;
  }) => void;
  placeholder?: string;
  showTimeSelect?: boolean;
  isRange?: boolean;
}

export default function ConfirmDatePicker({
  startDate,
  endDate,
  onDateChange,
  placeholder = "Select date and time",
  showTimeSelect = true,
  isRange = true,
}: ConfirmDatePickerProps) {
  const [selectedStartDate, setSelectedStartDate] = useState<Date | null>(
    startDate ? new Date(startDate) : null
  );
  const [selectedEndDate, setSelectedEndDate] = useState<Date | null>(
    endDate ? new Date(endDate) : null
  );
  const [selectedStartTime, setSelectedStartTime] = useState<Date | null>(
    startDate ? new Date(startDate) : null
  );
  const [selectedEndTime, setSelectedEndTime] = useState<Date | null>(
    endDate ? new Date(endDate) : null
  );

  // Combine date and time into full datetime
  const combineDateTime = (
    date: Date | null,
    time: Date | null
  ): Date | null => {
    if (!date) return null;
    if (!time) return date;

    const combined = new Date(date);
    combined.setHours(time.getHours());
    combined.setMinutes(time.getMinutes());
    combined.setSeconds(0);
    combined.setMilliseconds(0);
    return combined;
  };

  // Update parent component when dates/times change
  useEffect(() => {
    const combinedStartDate = combineDateTime(
      selectedStartDate,
      selectedStartTime
    );
    const combinedEndDate = combineDateTime(selectedEndDate, selectedEndTime);

    if (combinedStartDate || combinedEndDate) {
      onDateChange?.({
        startDate: combinedStartDate,
        endDate: combinedEndDate,
      });
    }
  }, [
    selectedStartDate,
    selectedStartTime,
    selectedEndDate,
    selectedEndTime,
    onDateChange,
  ]);

  const handleStartDateChange = (date: Date | null) => {
    setSelectedStartDate(date);
  };

  const handleEndDateChange = (date: Date | null) => {
    setSelectedEndDate(date);
  };

  const handleStartTimeChange = (time: Date | null) => {
    setSelectedStartTime(time);
  };

  const handleEndTimeChange = (time: Date | null) => {
    setSelectedEndTime(time);
  };

  return (
    <div className="w-full space-y-4">
      <div className="grid grid-cols-2 gap-4">
        {/* Start Date */}
        <div className="space-y-2">
          <label className="block text-sm font-medium text-gray-300">
            Start Date
          </label>
          <div className="relative">
            <DatePicker
              selected={selectedStartDate}
              onChange={handleStartDateChange}
              dateFormat="MMM d, yyyy"
              placeholderText="Select start date"
              className="w-full px-3 py-2 pl-10 text-sm bg-white border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              popperClassName="react-datepicker-popper"
              calendarClassName="shadow-lg border border-gray-200 rounded-lg"
            />
            <CalendarDaysIcon className="absolute left-3 top-2.5 w-4 h-4 text-gray-400" />
          </div>
        </div>

        {/* Start Time */}
        <div className="space-y-2">
          <label className="block text-sm font-medium text-gray-300">
            Start Time
          </label>
          <div className="relative">
            <DatePicker
              selected={selectedStartTime}
              onChange={handleStartTimeChange}
              showTimeSelect
              showTimeSelectOnly
              timeIntervals={15}
              timeCaption="Time"
              dateFormat="h:mm aa"
              placeholderText="Select start time"
              className="w-full px-3 py-2 pl-10 text-sm bg-white border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              popperClassName="react-datepicker-popper"
              calendarClassName="shadow-lg border border-gray-200 rounded-lg"
            />
            <ClockIcon className="absolute left-3 top-2.5 w-4 h-4 text-gray-400" />
          </div>
        </div>

        {/* End Date */}
        <div className="space-y-2">
          <label className="block text-sm font-medium text-gray-300">
            End Date
          </label>
          <div className="relative">
            <DatePicker
              selected={selectedEndDate}
              onChange={handleEndDateChange}
              dateFormat="MMM d, yyyy"
              placeholderText="Select end date"
              minDate={selectedStartDate || undefined} // Prevent selecting end date before start date
              className="w-full px-3 py-2 pl-10 text-sm bg-white border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              popperClassName="react-datepicker-popper"
              calendarClassName="shadow-lg border border-gray-200 rounded-lg"
            />
            <CalendarDaysIcon className="absolute left-3 top-2.5 w-4 h-4 text-gray-400" />
          </div>
        </div>

        {/* End Time */}
        <div className="space-y-2">
          <label className="block text-sm font-medium text-gray-300">
            End Time
          </label>
          <div className="relative">
            <DatePicker
              selected={selectedEndTime}
              onChange={handleEndTimeChange}
              showTimeSelect
              showTimeSelectOnly
              timeIntervals={15}
              timeCaption="Time"
              dateFormat="h:mm aa"
              placeholderText="Select end time"
              className="w-full px-3 py-2 pl-10 text-sm bg-white border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              popperClassName="react-datepicker-popper"
              calendarClassName="shadow-lg border border-gray-200 rounded-lg"
            />
            <ClockIcon className="absolute left-3 top-2.5 w-4 h-4 text-gray-400" />
          </div>
        </div>
      </div>

      {/* Summary Display */}
      {(selectedStartDate || selectedEndDate) && (
        <div className="mt-4 p-3 bg-gray-50 rounded-lg border">
          <h4 className="text-sm font-medium text-gray-700 mb-2">
            Selected Time Range:
          </h4>
          <div className="text-sm text-gray-600">
            {selectedStartDate && selectedStartTime && (
              <div>
                <strong>Start:</strong>{" "}
                {combineDateTime(
                  selectedStartDate,
                  selectedStartTime
                )?.toLocaleString()}
              </div>
            )}
            {selectedEndDate && selectedEndTime && (
              <div>
                <strong>End:</strong>{" "}
                {combineDateTime(
                  selectedEndDate,
                  selectedEndTime
                )?.toLocaleString()}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Custom styles for the datepicker */}
      <style jsx global>{`
        .react-datepicker-popper {
          z-index: 9999 !important;
        }

        .react-datepicker {
          font-family: inherit;
          border: 1px solid #e5e7eb;
          border-radius: 0.5rem;
          box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1),
            0 4px 6px -2px rgba(0, 0, 0, 0.05);
        }

        .react-datepicker__header {
          background-color: #f9fafb;
          border-bottom: 1px solid #e5e7eb;
          border-radius: 0.5rem 0.5rem 0 0;
        }

        .react-datepicker__current-month {
          color: #374151;
          font-weight: 600;
        }

        .react-datepicker__day {
          color: #374151;
          border-radius: 0.375rem;
          margin: 0.125rem;
        }

        .react-datepicker__day:hover {
          background-color: #dbeafe;
          color: #1d4ed8;
        }

        .react-datepicker__day--selected {
          background-color: #3b82f6;
          color: white;
        }

        .react-datepicker__time-container {
          border-left: 1px solid #e5e7eb;
        }

        .react-datepicker__time-list-item:hover {
          background-color: #dbeafe;
        }

        .react-datepicker__time-list-item--selected {
          background-color: #3b82f6;
          color: white;
        }
      `}</style>
    </div>
  );
}
