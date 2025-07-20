import { render, screen, cleanup, fireEvent } from "@testing-library/react";
import PreviousButton from "@/components/datepicker/PreviousButton";

afterEach(() => {
  cleanup();
})

test("renders next button", () => {
  const onClick = jest.fn();
  render(<PreviousButton onClick={onClick}/>);
  const buttonElement = screen.getByTestId('previousbutton');
  expect(buttonElement).toBeInTheDocument();
  fireEvent.click(buttonElement);
  expect(onClick).toHaveBeenCalledTimes(1);
});