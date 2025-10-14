import { render, screen, cleanup, fireEvent } from "@testing-library/react";
import EventDateSelector from "@/components/datepicker/EventDateSelector";

afterEach(() => {
  cleanup();
})

test("EventDateSelector renders correctly", () => {
  global.ResizeObserver = jest.fn().mockImplementation(() => ({
    observe: jest.fn(),
    unobserve: jest.fn(),
    disconnect: jest.fn(),
  }));
  
  const prevComponent = jest.fn();
  const nextComponent = jest.fn();
  const data = { start: null, end: null, event_name: "" };
  const setData = jest.fn();
  
  render(
    <EventDateSelector 
      prevComponent={prevComponent} 
      nextComponent={nextComponent} 
      data={data}
      setData={setData}
    />
  );
  
  const dateRangeElement = screen.getByTestId('daterangepicker');
  expect(dateRangeElement).toBeInTheDocument();
  
  // The component renders Start Date / End Date labels
  expect(screen.getByText("Start Date")).toBeInTheDocument();
  expect(screen.getByText("End Date")).toBeInTheDocument();
  
  // Check if the clear button is present
  expect(screen.getByText("Clear Dates")).toBeInTheDocument();
});

test("Navigation buttons are present", () => {
  global.ResizeObserver = jest.fn().mockImplementation(() => ({
    observe: jest.fn(),
    unobserve: jest.fn(),
    disconnect: jest.fn(),
  }));
  
  const prevComponent = jest.fn();
  const nextComponent = jest.fn();
  const data = { start: null, end: null, event_name: "" };
  const setData = jest.fn();
  
  render(
    <EventDateSelector 
      prevComponent={prevComponent} 
      nextComponent={nextComponent} 
      data={data}
      setData={setData}
    />
  );
  
  // Check if previous button is present
  expect(screen.getByText("Previous")).toBeInTheDocument();
  
  // Check if next button is present
  expect(screen.getByText("Next")).toBeInTheDocument();
});