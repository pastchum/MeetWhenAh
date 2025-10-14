import { render, screen, cleanup, fireEvent } from "@testing-library/react";
import EventForm from "@/components/datepicker/EventForm";

afterEach(() => {
  cleanup();
})

test("EventForm renders correctly", () => {
  const nextComponent = jest.fn();
  const data = { event_name: "", event_details: "" };
  const setData = jest.fn();
  
  render(<EventForm data={data} setData={setData} nextComponent={nextComponent} />);
  
  const detailElement = screen.getByTestId('details');
  expect(detailElement).toBeInTheDocument();
});

test("Event name input works", () => {
  const nextComponent = jest.fn();
  const data = { event_name: "", event_details: "" };
  const setData = jest.fn();
  
  render(<EventForm data={data} setData={setData} nextComponent={nextComponent} />);
  
  const nameInput = screen.getByPlaceholderText("Enter event name");
  expect(nameInput).toBeInTheDocument();
  
  fireEvent.change(nameInput, {target: {value: 'Test Event'}});
  // Assert updater was called with functional set and would set the value
  expect(setData).toHaveBeenCalled();
  const updater = setData.mock.calls[0][0];
  const updated = typeof updater === 'function' ? updater({ event_name: "", event_details: "" }) : {};
  expect(updated.event_name).toBe('Test Event');
});

test("Event details textarea works", () => {
  const nextComponent = jest.fn();
  const data = { event_name: "", event_details: "" };
  const setData = jest.fn();
  
  render(<EventForm data={data} setData={setData} nextComponent={nextComponent} />);
  
  const detailsTextarea = screen.getByPlaceholderText("Describe your event");
  expect(detailsTextarea).toBeInTheDocument();
  
  fireEvent.change(detailsTextarea, {target: {value: 'Test event details'}});
  expect(setData).toHaveBeenCalled();
  const updater2 = setData.mock.calls[setData.mock.calls.length - 1][0];
  const updated2 = typeof updater2 === 'function' ? updater2({ event_name: "", event_details: "" }) : {};
  expect(updated2.event_details).toBe('Test event details');
});

test("Next button is disabled when event name is empty", () => {
  const nextComponent = jest.fn();
  const data = { event_name: "", event_details: "" };
  const setData = jest.fn();
  
  render(<EventForm data={data} setData={setData} nextComponent={nextComponent} />);
  
  const nextButton = screen.getByTestId('nextbutton');
  expect(nextButton).toBeDisabled();
});

test("Next button is enabled when event name is filled", () => {
  const nextComponent = jest.fn();
  const data = { event_name: "Test Event", event_details: "" };
  const setData = jest.fn();
  
  render(<EventForm data={data} setData={setData} nextComponent={nextComponent} />);
  
  const nextButton = screen.getByTestId('nextbutton');
  expect(nextButton).not.toBeDisabled();
});