import { render, screen, cleanup, fireEvent } from "@testing-library/react";
import NextButton from "@/components/datepicker/NextButton";

afterEach(() => {
  cleanup();
})

test("renders and clicks date picker next button", () => {
  const onClick = jest.fn();
  render(<NextButton onClick={onClick}/>);
  const buttonElement = screen.getByTestId('nextbutton');
  expect(buttonElement).toBeInTheDocument();
  fireEvent.click(buttonElement);
  expect(onClick).toHaveBeenCalledTimes(1);
});
