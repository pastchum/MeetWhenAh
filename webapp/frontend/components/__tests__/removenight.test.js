import { render, screen, cleanup, fireEvent } from "@testing-library/react";
import RemoveNightButton from "@/components/dragselector/RemoveNightButton";

afterEach(() => {
  cleanup();
})

test("renders and clicks remove night button", () => {
  const onClick = jest.fn();
  render(<RemoveNightButton onClick={onClick}/>);
  const buttonElement = screen.getByText('Toggle full day');
  expect(buttonElement).toBeInTheDocument();
  fireEvent.click(buttonElement);
  expect(onClick).toHaveBeenCalledTimes(1);
});