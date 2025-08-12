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
  const initialData = { start: null, end: null };
  
  render(<EventDateSelector prevComponent={prevComponent} nextComponent={nextComponent} initialData={initialData} />);
  
  const dateRangeElement = screen.getByTestId('daterangepicker');
  expect(dateRangeElement).toBeInTheDocument();
  
  // Check if the date range picker label is present
  expect(screen.getByText("Event Date Range")).toBeInTheDocument();
  
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
  const initialData = { start: null, end: null };
  
  render(<EventDateSelector prevComponent={prevComponent} nextComponent={nextComponent} initialData={initialData} />);
  
  // Check if previous button is present
  expect(screen.getByText("Previous")).toBeInTheDocument();
  
  // Check if next button is present
  expect(screen.getByText("Next")).toBeInTheDocument();
});