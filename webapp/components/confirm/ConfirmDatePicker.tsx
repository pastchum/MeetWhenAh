import { useState, useEffect } from "react";
import { CalendarDaysIcon, ClockIcon } from "@heroicons/react/24/outline";
import {
  DatePicker,
  Label,
  Group,
  DateInput,
  Button,
  Popover,
  Dialog,
  Calendar,
  CalendarGrid,
  CalendarCell,
  CalendarGridHeader,
  CalendarGridBody,
  CalendarHeaderCell,
  Heading,
  DateSegment,
  TimeField,
} from "react-aria-components";
import {
  CalendarDate,
  CalendarDateTime,
  parseDate,
  parseDateTime,
  today,
  getLocalTimeZone,
  Time,
} from "@internationalized/date";

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
  const [selectedStartDate, setSelectedStartDate] =
    useState<CalendarDate | null>(
      startDate
        ? parseDate(new Date(startDate).toISOString().split("T")[0])
        : null
    );
  const [selectedEndDate, setSelectedEndDate] = useState<CalendarDate | null>(
    endDate ? parseDate(new Date(endDate).toISOString().split("T")[0]) : null
  );
  const [selectedStartTime, setSelectedStartTime] = useState<Time | null>(
    startDate
      ? new Time(
          new Date(startDate).getHours(),
          new Date(startDate).getMinutes()
        )
      : null
  );
  const [selectedEndTime, setSelectedEndTime] = useState<Time | null>(
    endDate
      ? new Time(new Date(endDate).getHours(), new Date(endDate).getMinutes())
      : null
  );

  // Convert CalendarDate and Time to Date
  const combineDateTime = (
    date: CalendarDate | null,
    time: Time | null
  ): Date | null => {
    if (!date) return null;
    if (!time) {
      return new Date(date.year, date.month - 1, date.day);
    }

    return new Date(
      date.year,
      date.month - 1,
      date.day,
      time.hour,
      time.minute
    );
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

  const handleStartDateChange = (date: CalendarDate | null) => {
    setSelectedStartDate(date);
  };

  const handleEndDateChange = (date: CalendarDate | null) => {
    setSelectedEndDate(date);
  };

  const handleStartTimeChange = (time: Time | null) => {
    setSelectedStartTime(time);
  };

  const handleEndTimeChange = (time: Time | null) => {
    setSelectedEndTime(time);
  };

  return (
    <div className="w-full space-y-4">
      <div className="grid grid-cols-2 gap-4 text-gray-700">
        {/* Start Date */}
        <div className="space-y-2">
          <Label className="block text-sm font-medium text-slate-300">
            Start Date
          </Label>
          <div className="relative">
            <DatePicker
              value={selectedStartDate}
              onChange={handleStartDateChange}
            >
              <Group className="flex">
                <DateInput className="w-full px-3 py-2 pl-10 text-sm bg-white border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-red-500">
                  {(segment) => (
                    <DateSegment
                      segment={segment}
                      className="px-0.5 tabular-nums outline-none rounded-sm focus:bg-red-600 focus:text-slate-500 caret-transparent placeholder-shown:text-gray-500 text-gray-800"
                    />
                  )}
                </DateInput>
                <Button className="ml-1 p-1 rounded outline-none focus:ring-2 focus:ring-red-500">
                  <CalendarDaysIcon className="absolute left-3 top-2.5 w-4 h-4 text-gray-400" />
                </Button>
              </Group>
              <Popover
                placement="top"
                className="bg-slate-50 border border-slate-200 rounded-lg shadow-lg z-[999999] p-4"
              >
                <Dialog>
                  <Calendar>
                    <header className="flex items-center gap-1 pb-4 px-1 text-slate-500 w-full">
                      <Heading className="flex-1 font-semibold text-2xl ml-2 text-slate-700" />
                      <Button
                        slot="previous"
                        className="w-9 h-9 outline-none cursor-default bg-transparent text-slate-500 border-0 flex items-center justify-center rounded-full hover:bg-slate-50 focus:ring-2 focus:ring-red-500"
                      >
                        ◀
                      </Button>
                      <Button
                        slot="next"
                        className="w-9 h-9 outline-none cursor-default bg-transparent text-slate-500 border-0 flex items-center justify-center rounded-full hover:bg-slate-50 focus:ring-2 focus:ring-red-500"
                      >
                        ▶
                      </Button>
                    </header>
                    <CalendarGrid className="border-spacing-1 border-separate">
                      <CalendarGridHeader>
                        {(day) => (
                          <CalendarHeaderCell className="text-xs text-slate-500 font-semibold">
                            {day}
                          </CalendarHeaderCell>
                        )}
                      </CalendarGridHeader>
                      <CalendarGridBody>
                        {(date) => (
                          <CalendarCell
                            date={date}
                            className="w-9 h-9 outline-none cursor-default rounded-full flex items-center justify-center text-slate-800 outside-month:text-slate-500 hover:bg-slate-50 pressed:bg-slate-100 selected:bg-red-600 selected:text-slate-500 focus:ring-2 focus:ring-red-500"
                          />
                        )}
                      </CalendarGridBody>
                    </CalendarGrid>
                  </Calendar>
                </Dialog>
              </Popover>
            </DatePicker>
          </div>
        </div>

        {/* Start Time */}
        <div className="space-y-2">
          <Label className="block text-sm font-medium text-slate-300">
            Start Time
          </Label>
          <div className="relative">
            <TimeField
              value={selectedStartTime}
              onChange={handleStartTimeChange}
              className="w-full"
            >
              <DateInput className="w-full px-3 py-2 pl-10 text-sm bg-white border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-red-500">
                {(segment) => (
                  <DateSegment
                    segment={segment}
                    className="px-0.5 tabular-nums outline-none rounded-sm focus:bg-red-600 focus:text-slate-500 caret-transparent placeholder-shown:text-gray-500 text-gray-800"
                  />
                )}
              </DateInput>
            </TimeField>
            <ClockIcon className="absolute left-3 top-2.5 w-4 h-4 text-gray-400 pointer-events-none" />
          </div>
        </div>

        {/* End Date */}
        <div className="space-y-2">
          <Label className="block text-sm font-medium text-slate-300">
            End Date
          </Label>
          <div className="relative">
            <DatePicker
              value={selectedEndDate}
              onChange={handleEndDateChange}
              minValue={selectedStartDate || undefined}
            >
              <Group className="flex">
                <DateInput className="w-full px-3 py-2 pl-10 text-sm bg-white border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-red-500">
                  {(segment) => (
                    <DateSegment
                      segment={segment}
                      className="px-0.5 tabular-nums outline-none rounded-sm focus:bg-red-600 focus:text-slate-500 caret-transparent placeholder-shown:text-gray-500 text-gray-800"
                    />
                  )}
                </DateInput>
                <Button className="ml-1 p-1 rounded outline-none focus:ring-2 focus:ring-red-500">
                  <CalendarDaysIcon className="absolute left-3 top-2.5 w-4 h-4 text-gray-400" />
                </Button>
              </Group>
              <Popover
                placement="top"
                className="bg-slate-50 border border-slate-200 rounded-lg shadow-lg z-[999999] p-4"
              >
                <Dialog>
                  <Calendar>
                    <header className="flex items-center gap-1 pb-4 px-1 w-full text-slate-800">
                      <Heading className="flex-1 font-semibold text-2xl ml-2" />
                      <Button
                        slot="previous"
                        className="w-9 h-9 outline-none cursor-default bg-transparent text-gray-600 border-0 flex items-center justify-center rounded-full hover:bg-gray-100 focus:ring-2 focus:ring-red-500"
                      >
                        ◀
                      </Button>
                      <Button
                        slot="next"
                        className="w-9 h-9 outline-none cursor-default bg-transparent text-gray-600 border-0 flex items-center justify-center rounded-full hover:bg-gray-100 focus:ring-2 focus:ring-red-500"
                      >
                        ▶
                      </Button>
                    </header>
                    <CalendarGrid className="border-spacing-1 border-separate">
                      <CalendarGridHeader>
                        {(day) => (
                          <CalendarHeaderCell className="text-xs text-slate-800 outside-month:text-gray-300 font-semibold">
                            {day}
                          </CalendarHeaderCell>
                        )}
                      </CalendarGridHeader>
                      <CalendarGridBody>
                        {(date) => (
                          <CalendarCell
                            date={date}
                            className="w-9 h-9 outline-none cursor-default rounded-full flex items-center justify-center text-slate-800 outside-month:text-gray-300 hover:bg-gray-100 pressed:bg-gray-200 selected:bg-red-600 selected:text-slate-500 focus:ring-2 focus:ring-red-500"
                          />
                        )}
                      </CalendarGridBody>
                    </CalendarGrid>
                  </Calendar>
                </Dialog>
              </Popover>
            </DatePicker>
          </div>
        </div>

        {/* End Time */}
        <div className="space-y-2">
          <Label className="block text-sm font-medium text-slate-300">
            End Time
          </Label>
          <div className="relative">
            <TimeField
              value={selectedEndTime}
              onChange={handleEndTimeChange}
              className="w-full"
            >
              <DateInput className="w-full px-3 py-2 pl-10 text-sm bg-slate-50 border border-slate-200 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-red-500">
                {(segment) => (
                  <DateSegment
                    segment={segment}
                    className="px-0.5 tabular-nums outline-none rounded-sm focus:bg-red-600 focus:text-slate-500 caret-transparent placeholder-shown:text-gray-500 text-gray-800"
                  />
                )}
              </DateInput>
            </TimeField>
            <ClockIcon className="absolute left-3 top-2.5 w-4 h-4 text-gray-400 pointer-events-none" />
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
    </div>
  );
}
