import { render, screen, cleanup, fireEvent } from "@testing-library/react";
import PreviousButton from "@/components/dragselector/PreviousButton";

afterEach(() => {
  cleanup();
})

test("renders and clicks previous button", () => {
  const onClick = jest.fn();
  render(<PreviousButton onClick={onClick}/>);
  const buttonElement = screen.getByTestId('previousbutton2');
  expect(buttonElement).toBeInTheDocument();
  fireEvent.click(buttonElement);
  expect(onClick).toHaveBeenCalledTimes(1);
});