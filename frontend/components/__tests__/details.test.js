import { render, screen, cleanup, fireEvent } from "@testing-library/react";
import Details from "@/components/datepicker/Details";
import Name from "@/components/datepicker/Details/Name";
import TextArea from "@/components/datepicker/Details/TextArea";

afterEach(() => {
  cleanup();
})

test("Details page works", () => {
  render(<Details/>);
  const detailElement = screen.getByTestId('details');
  expect(detailElement).toBeInTheDocument();
});

test("Name change works", () => {
  const handleInputChange = jest.fn();
  render(<Name handleInputChange={handleInputChange}/>);
  const detailElement = screen.getByPlaceholderText("Name of your event!");
  expect(detailElement).toBeInTheDocument();
  fireEvent.change(detailElement, {target: {value: 'aa'}});
  expect(handleInputChange).toHaveBeenCalledTimes(1);
});

test("Textarea change works", () => {
  const handleInputChange = jest.fn();
  render(<TextArea handleInputChange={handleInputChange}/>);
  const detailElement = screen.getByPlaceholderText("Details about your event");
  expect(detailElement).toBeInTheDocument();
  fireEvent.change(detailElement, {target: {value: 'aa'}});
  expect(handleInputChange).toHaveBeenCalledTimes(1);
});