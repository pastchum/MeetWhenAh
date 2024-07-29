import { render, screen, cleanup } from "@testing-library/react";
import Box from "@/components/dragselector/Box";

afterEach(() => {
  cleanup();
})

test("renders box", () => {
  const date = new Date("2022-03-25");
  render(<Box date={date} time="0000" appendMode={false} />);
  const buttonElement = screen.getByTestId('box');
  expect(buttonElement).toBeInTheDocument();
});