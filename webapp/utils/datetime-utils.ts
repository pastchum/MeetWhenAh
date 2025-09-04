/**
 * Date and time utility functions for consistent formatting across the app
 */

export interface DateTimeFormatOptions {
  showYear?: boolean;
  showTime?: boolean;
  showTimezone?: boolean;
  mobile?: boolean;
  format?: 'short' | 'medium' | 'long';
}

/**
 * Format timezone string to readable format (e.g., "SGT (GMT+8)")
 */
export function formatTimezone(timezone: string): string {
  if (!timezone) return '';
  
  try {
    // Common timezone mappings with abbreviations
    const timezoneMap: Record<string, { abbr: string; offset: string }> = {
      'Asia/Singapore': { abbr: 'SGT', offset: '+8' },
      'Asia/Tokyo': { abbr: 'JST', offset: '+9' },
      'Asia/Seoul': { abbr: 'KST', offset: '+9' },
      'Asia/Shanghai': { abbr: 'CST', offset: '+8' },
      'Asia/Hong_Kong': { abbr: 'HKT', offset: '+8' },
      'Asia/Bangkok': { abbr: 'ICT', offset: '+7' },
      'Asia/Jakarta': { abbr: 'WIB', offset: '+7' },
      'Asia/Kolkata': { abbr: 'IST', offset: '+5:30' },
      'Asia/Dubai': { abbr: 'GST', offset: '+4' },
      'Europe/London': { abbr: 'GMT', offset: '+0' },
      'Europe/Paris': { abbr: 'CET', offset: '+1' },
      'Europe/Berlin': { abbr: 'CET', offset: '+1' },
      'America/New_York': { abbr: 'EST', offset: '-5' },
      'America/Los_Angeles': { abbr: 'PST', offset: '-8' },
      'America/Chicago': { abbr: 'CST', offset: '-6' },
      'Australia/Sydney': { abbr: 'AEST', offset: '+10' },
      'Australia/Perth': { abbr: 'AWST', offset: '+8' },
      'Pacific/Auckland': { abbr: 'NZST', offset: '+12' }
    };

    // Check if we have a mapping for this timezone
    if (timezoneMap[timezone]) {
      const { abbr, offset } = timezoneMap[timezone];
      return `${abbr} [GMT${offset}]`;
    }

    // Handle UTC/GMT formats
    if (timezone.includes('UTC') || timezone.includes('GMT')) {
      if (timezone.includes('+')) {
        const offset = timezone.match(/\+(\d+)/)?.[1];
        return offset ? `GMT+${offset}` : timezone;
      } else if (timezone.includes('-')) {
        const offset = timezone.match(/-(\d+)/)?.[1];
        return offset ? `GMT-${offset}` : timezone;
      }
      return 'GMT+0';
    }

    // Try to extract offset from timezone string
    const offsetMatch = timezone.match(/([+-]\d{1,2}(?::\d{2})?)/);
    if (offsetMatch) {
      const offset = offsetMatch[1];
      // Try to get a short abbreviation from the timezone
      const parts = timezone.split('/');
      const lastPart = parts[parts.length - 1]?.replace(/_/g, '');
      if (lastPart && lastPart.length <= 4) {
        return `${lastPart.toUpperCase()} [GMT${offset}]`;
      }
      return `GMT${offset}`;
    }

    // Fallback: return timezone abbreviation if it's short
    if (timezone.length <= 6) {
      return timezone.toUpperCase();
    }

    // Last resort: return original timezone
    return timezone;
  } catch (error) {
    // Fallback to original timezone string
    return timezone;
  }
}

/**
 * Format date and time for mobile display
 */
export function formatDateTime(
  dateStr: string, 
  timeStr: string, 
  timezone?: string,
  options: DateTimeFormatOptions = {}
): string {
  const {
    showYear = true,
    showTime = true,
    showTimezone = true,
    mobile = true,
    format = 'short'
  } = options;

  try {
    const date = new Date(dateStr);
    const time = timeStr.split('T')[1]?.split('.')[0] || timeStr;
    
    // Mobile-friendly date formatting
    let dateFormat: Intl.DateTimeFormatOptions;
    
    if (mobile) {
      if (format === 'short') {
        dateFormat = { 
          month: 'short', 
          day: 'numeric'
        };
      } else if (format === 'medium') {
        dateFormat = { 
          month: 'short', 
          day: 'numeric',
          year: 'numeric'
        };
      } else {
        dateFormat = { 
          weekday: 'short',
          month: 'short', 
          day: 'numeric',
          year: 'numeric'
        };
      }
    } else {
      dateFormat = { 
        month: 'short', 
        day: 'numeric',
        year: 'numeric'
      };
    }
    
    const formattedDate = date.toLocaleDateString('en-US', dateFormat);
    
    if (!showTime) {
      return formattedDate;
    }
    
    // Mobile-friendly time formatting
    let formattedTime: string;
    if (mobile) {
      // Remove seconds, keep only HH:MM
      formattedTime = time.substring(0, 5);
    } else {
      // Include seconds for desktop
      formattedTime = time.substring(0, 8);
    }
    
    let result = `${formattedDate} at ${formattedTime}`;
    
    // Add timezone if requested and available
    if (showTimezone && timezone) {
      const tzFormatted = formatTimezone(timezone);
      if (tzFormatted) {
        result += ` ${tzFormatted}`;
      }
    }
    
    return result;
  } catch (error) {
    console.error('Error formatting date/time:', error);
    return `${dateStr} ${timeStr}`;
  }
}

/**
 * Format date range for mobile display
 */
export function formatDateRange(
  startDate: string,
  endDate: string,
  startTime: string,
  endTime: string,
  timezone?: string,
  options: DateTimeFormatOptions = {}
): string {
  const {
    showYear = true,
    mobile = true,
    format = 'short'
  } = options;

  try {
    const start = new Date(startDate);
    const end = new Date(endDate);
    
    // Check if same day
    const isSameDay = start.toDateString() === end.toDateString();
    
    if (isSameDay) {
      // Same day: "Dec 15 at 09:00 - 17:00 GMT+8 Singapore"
      const datePart = formatDateTime(startDate, startTime, timezone, { 
        showTime: false, 
        showTimezone: false,
        mobile,
        format 
      });
      const startTimeFormatted = startTime.substring(0, 5);
      const endTimeFormatted = endTime.substring(0, 5);
      
      let result = `${datePart} at ${startTimeFormatted} - ${endTimeFormatted}`;
      
      if (timezone) {
        const tzFormatted = formatTimezone(timezone);
        if (tzFormatted) {
          result += ` ${tzFormatted}`;
        }
      }
      
      return result;
    } else {
      // Different days: "Dec 15 at 09:00 - Dec 16 at 17:00 GMT+8 Singapore"
      const startFormatted = formatDateTime(startDate, startTime, timezone, { 
        showTimezone: false,
        mobile,
        format 
      });
      const endFormatted = formatDateTime(endDate, endTime, timezone, { 
        showTimezone: false,
        mobile,
        format 
      });
      
      let result = `${startFormatted} - ${endFormatted}`;
      
      if (timezone) {
        const tzFormatted = formatTimezone(timezone);
        if (tzFormatted) {
          result += ` ${tzFormatted}`;
        }
      }
      
      return result;
    }
  } catch (error) {
    console.error('Error formatting date range:', error);
    return `${startDate} ${startTime} - ${endDate} ${endTime}`;
  }
}

/**
 * Format relative time (e.g., "2 hours ago", "in 3 days")
 */
export function formatRelativeTime(dateStr: string): string {
  try {
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);
    
    if (diffMins < 1) return 'just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    
    // For longer periods, use date formatting
    return formatDateTime(dateStr, '00:00:00', undefined, { 
      showTime: false, 
      showYear: true,
      mobile: true,
      format: 'short'
    });
  } catch (error) {
    console.error('Error formatting relative time:', error);
    return dateStr;
  }
}

/**
 * Check if date is today
 */
export function isToday(dateStr: string): boolean {
  try {
    const date = new Date(dateStr);
    const today = new Date();
    return date.toDateString() === today.toDateString();
  } catch (error) {
    return false;
  }
}

/**
 * Check if date is tomorrow
 */
export function isTomorrow(dateStr: string): boolean {
  try {
    const date = new Date(dateStr);
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    return date.toDateString() === tomorrow.toDateString();
  } catch (error) {
    return false;
  }
}

/**
 * Get mobile-friendly day label
 */
export function getDayLabel(dateStr: string): string {
  if (isToday(dateStr)) return 'Today';
  if (isTomorrow(dateStr)) return 'Tomorrow';
  
  try {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { weekday: 'short' });
  } catch (error) {
    return '';
  }
}

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

/**
 * Format duration in blocks to human-readable format
 */
export function formatDurationBlocks(minBlocks: number, maxBlocks: number): string {
  if (minBlocks === maxBlocks) {
    return `${minBlocks} block${minBlocks !== 1 ? 's' : ''}`;
  }
  return `${minBlocks} - ${maxBlocks} blocks`;
}

/**
 * Format time only (HH:MM format)
 */
export function formatTimeOnly(timeStr: string): string {
  try {
    const time = timeStr.split('T')[1]?.split('.')[0] || timeStr;
    return time.substring(0, 5); // HH:MM format
  } catch (error) {
    return timeStr;
  }
}

/**
 * Check if two dates are the same day
 */
export function isSameDay(date1: string, date2: string): boolean {
  try {
    const d1 = new Date(date1);
    const d2 = new Date(date2);
    return d1.toDateString() === d2.toDateString();
  } catch (error) {
    return false;
  }
}

/**
 * Get compact date format for mobile (e.g., "Today", "Tomorrow", "Dec 15")
 */
export function getCompactDateLabel(dateStr: string): string {
  if (isToday(dateStr)) return 'Today';
  if (isTomorrow(dateStr)) return 'Tomorrow';
  
  try {
    const date = new Date(dateStr);
    const now = new Date();
    const diffTime = date.getTime() - now.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays > 0 && diffDays <= 7) {
      return date.toLocaleDateString('en-US', { weekday: 'short' });
    }
    
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric' 
    });
  } catch (error) {
    return '';
  }
} 