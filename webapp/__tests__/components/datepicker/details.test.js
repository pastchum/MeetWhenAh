import { render, screen, cleanup, fireEvent } from "@testing-library/react";
import EventForm from "@/components/datepicker/EventForm";

afterEach(() => {
  cleanup();
})

test("EventForm renders correctly", () => {
  const nextComponent = jest.fn();
  const initialData = { event_name: "", event_details: "" };
  
  render(<EventForm initialData={initialData} nextComponent={nextComponent} />);
  
  const detailElement = screen.getByTestId('details');
  expect(detailElement).toBeInTheDocument();
});

test("Event name input works", () => {
  const nextComponent = jest.fn();
  const initialData = { event_name: "", event_details: "" };
  
  render(<EventForm initialData={initialData} nextComponent={nextComponent} />);
  
  const nameInput = screen.getByPlaceholderText("Enter event name");
  expect(nameInput).toBeInTheDocument();
  
  fireEvent.change(nameInput, {target: {value: 'Test Event'}});
  expect(nameInput.value).toBe('Test Event');
});

test("Event details textarea works", () => {
  const nextComponent = jest.fn();
  const initialData = { event_name: "", event_details: "" };
  
  render(<EventForm initialData={initialData} nextComponent={nextComponent} />);
  
  const detailsTextarea = screen.getByPlaceholderText("Describe your event");
  expect(detailsTextarea).toBeInTheDocument();
  
  fireEvent.change(detailsTextarea, {target: {value: 'Test event details'}});
  expect(detailsTextarea.value).toBe('Test event details');
});

test("Next button is disabled when event name is empty", () => {
  const nextComponent = jest.fn();
  const initialData = { event_name: "", event_details: "" };
  
  render(<EventForm initialData={initialData} nextComponent={nextComponent} />);
  
  const nextButton = screen.getByTestId('nextbutton');
  expect(nextButton).toBeDisabled();
});

test("Next button is enabled when event name is filled", () => {
  const nextComponent = jest.fn();
  const initialData = { event_name: "Test Event", event_details: "" };
  
  render(<EventForm initialData={initialData} nextComponent={nextComponent} />);
  
  const nextButton = screen.getByTestId('nextbutton');
  expect(nextButton).not.toBeDisabled();
});