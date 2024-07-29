import { render, screen, cleanup, fireEvent } from "@testing-library/react";
import NextButton from "@/components/dragselector/NextButton";

afterEach(() => {
  cleanup();
})

test("renders dragselector nextbutton", () => {
  const onClick = jest.fn();
  render(<NextButton onClick={onClick}/>);
  const buttonElement = screen.getByTestId('nextbutton2');
  expect(buttonElement).toBeInTheDocument();
  fireEvent.click(buttonElement);
  expect(onClick).toHaveBeenCalledTimes(1);
});