/**
 * Unified datetime utilities for the MeetWhenAh app
 * All times are stored in UTC and converted to/from user's local timezone for display
 */

/**
 * Convert day (YYYY-MM-DD) and time (minutes from midnight) to UTC datetime string
 * Input is treated as user's local timezone, output is UTC for storage
 */
export function getUtcDatetime(day: string, timeMinutes: number): string {
  const [year, month, date] = day.split("-").map(Number);
  const hours = Math.floor(timeMinutes / 60);
  const minutes = timeMinutes % 60;

  // Create date in user's local timezone, then convert to UTC
  const localDate = new Date(year, month - 1, date, hours, minutes);
  return localDate.toISOString();
}

/**
 * Convert UTC datetime string back to local day and time
 * Input is UTC from storage, output is user's local timezone for display
 */
export function getLocalDayAndTime(utcString: string): { day: string; time: number } {
  const date = new Date(utcString);
  
  // Get local timezone values (not UTC)
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const dayOfMonth = String(date.getDate()).padStart(2, '0');
  const day = `${year}-${month}-${dayOfMonth}`;
  
  const time = date.getHours() * 60 + date.getMinutes();
  
  return { day, time };
}

/**
 * Format minutes as HH:MM string
 */
export function formatTime(minutes: number): string {
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  return `${hours.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}`;
}

/**
 * Check if a time slot is selected by comparing against selectedSlots
 * Handles UTC conversion properly
 */
export function isSlotSelected(
  dayKey: string, 
  time: number, 
  selectedSlots: Set<string>
): boolean {
  const utcDatetime = getUtcDatetime(dayKey, time);
  return selectedSlots.has(utcDatetime);
}

// Legacy function names for backward compatibility - will be removed after migration
export const getIsoDatetime = getUtcDatetime;
export const getDayAndTimeFromIso = getLocalDayAndTime; 