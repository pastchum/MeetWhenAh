import { render, screen, cleanup } from "@testing-library/react";
import Summary from '../datepicker/Summary';

afterEach(() => {
  cleanup();
})

test("summary works", () => {
  const data = {
    event_name: "name",
    event_details: "detail1",
    start: 11/11/11,
    end: 22/22/22 
  };
  render(<Summary data={data}/>);
  const summaryElement = screen.getByTestId('summary');
  expect(summaryElement).toBeInTheDocument();
  expect(screen.getByText(data.event_name)).toBeInTheDocument();
  expect(screen.getByText(data.event_details)).toBeInTheDocument();
  expect(screen.getByText(data.start.toString())).toBeInTheDocument();
  expect(screen.getByText(data.end.toString())).toBeInTheDocument();
});