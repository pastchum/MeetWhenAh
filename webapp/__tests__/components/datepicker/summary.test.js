import { render, screen, cleanup } from "@testing-library/react";
import ReviewSubmit from "@/components/datepicker/ReviewSubmit";

afterEach(() => {
  cleanup();
})

test("ReviewSubmit component renders correctly with event data", () => {
  const data = {
    event_name: "Test Event",
    event_details: "Test event details",
    start: "2024-01-15",
    end: "2024-01-20"
  };
  
  const prevComponent = jest.fn();
  
  render(<ReviewSubmit data={data} prevComponent={prevComponent} />);
  
  // Check if the main component renders
  const summaryElement = screen.getByTestId('summary');
  expect(summaryElement).toBeInTheDocument();
  
  // Check if event data is displayed
  expect(screen.getByText(data.event_name)).toBeInTheDocument();
  expect(screen.getByText(data.event_details)).toBeInTheDocument();
  expect(screen.getByText(data.start)).toBeInTheDocument();
  expect(screen.getByText(data.end)).toBeInTheDocument();
  
  // Check if submit button is present
  expect(screen.getByText("Submit")).toBeInTheDocument();
  
  // Check if previous button is present
  expect(screen.getByText("Previous")).toBeInTheDocument();
});