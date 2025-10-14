import { computeWeekWindow } from "@/utils/datetime-utils";

describe("computeWeekWindow", () => {
  it("uses event start if today is before event start", () => {
    const eventStart = "2025-10-20T00:00:00.000Z";
    const eventEnd = "2025-11-05T00:00:00.000Z";
    const today = new Date("2025-10-10T12:00:00.000Z");

    const { weekStart, weekEnd } = computeWeekWindow(eventStart, eventEnd, today);

    expect(weekStart.toISOString()).toBe(new Date(eventStart).toISOString());
    // 7 days from eventStart
    expect(weekEnd.toISOString()).toBe(new Date("2025-10-27T00:00:00.000Z").toISOString());
  });

  it("uses today if today is after event start but before event end", () => {
    const eventStart = "2025-10-01T00:00:00.000Z";
    const eventEnd = "2025-10-30T00:00:00.000Z";
    const today = new Date("2025-10-15T09:30:00.000Z");

    const { weekStart, weekEnd } = computeWeekWindow(eventStart, eventEnd, today);

    expect(weekStart.toISOString()).toBe(today.toISOString());
    const expectedEnd = new Date(today.getTime() + 7 * 24 * 60 * 60 * 1000);
    expect(weekEnd.toISOString()).toBe(expectedEnd.toISOString());
  });

  it("clamps week end to event end if within 7 days", () => {
    const eventStart = "2025-10-01T00:00:00.000Z";
    const eventEnd = "2025-10-18T00:00:00.000Z"; // 3 days after 'today'
    const today = new Date("2025-10-15T00:00:00.000Z");

    const { weekStart, weekEnd } = computeWeekWindow(eventStart, eventEnd, today);

    expect(weekStart.toISOString()).toBe(today.toISOString());
    expect(weekEnd.toISOString()).toBe(new Date(eventEnd).toISOString());
  });

  it("handles today exactly at event start", () => {
    const eventStart = "2025-10-15T00:00:00.000Z";
    const eventEnd = "2025-11-01T00:00:00.000Z";
    const today = new Date("2025-10-15T00:00:00.000Z");

    const { weekStart, weekEnd } = computeWeekWindow(eventStart, eventEnd, today);

    expect(weekStart.toISOString()).toBe(eventStart);
    expect(weekEnd.toISOString()).toBe(new Date("2025-10-22T00:00:00.000Z").toISOString());
  });

  it("clamps when today is after event end (weekStart == weekEnd == eventEnd)", () => {
    const eventStart = "2025-10-01T00:00:00.000Z";
    const eventEnd = "2025-10-10T00:00:00.000Z";
    const today = new Date("2025-10-12T12:00:00.000Z");

    const { weekStart, weekEnd } = computeWeekWindow(eventStart, eventEnd, today);

    expect(weekStart.toISOString()).toBe(eventEnd);
    expect(weekEnd.toISOString()).toBe(eventEnd);
  });

  it("handles single-day event (start == end)", () => {
    const eventStart = "2025-10-20T00:00:00.000Z";
    const eventEnd = "2025-10-20T00:00:00.000Z";
    const today = new Date("2025-10-15T00:00:00.000Z");

    const { weekStart, weekEnd } = computeWeekWindow(eventStart, eventEnd, today);

    expect(weekStart.toISOString()).toBe(eventStart);
    expect(weekEnd.toISOString()).toBe(eventEnd);
  });
});


