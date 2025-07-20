import { render, screen, cleanup } from "@testing-library/react";
import CustomDateRangePicker from "@/components/datepicker/CustomDateRangePicker";

afterEach(() => {
  cleanup();
})

test("Custom date range picker renders", () => {
  global.ResizeObserver = jest.fn().mockImplementation(() => ({
    observe: jest.fn(),
    unobserve: jest.fn(),
    disconnect: jest.fn(),
}))
  render(<CustomDateRangePicker/>);
  const buttonElement = screen.getByTestId('daterangepicker');
  expect(buttonElement).toBeInTheDocument();
});