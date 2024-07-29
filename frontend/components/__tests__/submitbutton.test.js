import { render, screen, cleanup, fireEvent } from "@testing-library/react";
import SubmitButton from "@/components/dragselector/SubmitButton";

afterEach(() => {
  cleanup();
})

test("renders submit button", () => {
  render(<SubmitButton/>);
  const buttonElement = screen.getByTestId('submitbutton');
  expect(buttonElement).toBeInTheDocument();
});

test("clicks submit button", () => {
  const onClick = jest.fn();
  render(<SubmitButton onClick={onClick}/>);
  const buttonElement = screen.getByTestId('submitbutton');
  expect(buttonElement).toBeInTheDocument();
  fireEvent.click(buttonElement);
  expect(onClick).toHaveBeenCalledTimes(1);
});
