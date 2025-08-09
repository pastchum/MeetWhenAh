# WeekCalendar Data Flow Analysis

## Overview
This document provides a deep dive into the data flow for availability and event selection in the MeetWhenAh application, specifically focusing on the WeekCalendar component and its dependencies.

## Core Components

### 1. WeekCalendar Component (`webapp/components/dragselector/WeekCalendar.tsx`)
The main orchestrator that manages:
- Time slot selection state
- Drag operations
- Backend synchronization
- Visual rendering

### 2. TimeGrid Component (`webapp/components/dragselector/TimeGrid.tsx`)
Renders the grid of time slots and handles:
- Individual slot rendering
- Selection state checking
- Event propagation to parent

### 3. TimeSlot Component (`webapp/components/dragselector/TimeSlot.tsx`)
Individual time slot that handles:
- Mouse/touch interactions
- Visual state (selected/unselected)
- Drag start/over/end events

## Data Flow Architecture

### 1. Time Representation System

#### Internal Format: UTC ISO Datetime Strings
- **Primary Format**: UTC ISO 8601 datetime strings with `.000Z` suffix (e.g., `"2024-01-15T14:30:00.000Z"`)
- **Storage**: `Set<string>` containing UTC datetime strings
- **Consistent Format**: All datetime strings are normalized to UTC with `.000Z` format
- **Key Functions**:
  - `getUtcDatetime(day: string, timeMinutes: number)`: Converts local day/time to UTC ISO string
  - `getLocalDayAndTime(utcString: string)`: Extracts local day and time from UTC string
  - `isSlotSelected(dayKey: string, time: number, selectedSlots: Set<string>)`: Checks selection status

#### Time Slot Generation
```typescript
// 48 time slots per day (every 30 minutes from 00:00 to 23:30)
const timeSlots = Array.from({ length: 48 }, (_, i) => i * 30);
```

### 2. Selection State Management

#### State Structure
```typescript
const [selectedSlots, setSelectedSlots] = useState<Set<string>>(new Set());
```

#### Selection Operations
1. **Individual Slot Toggle**: `handleTapToToggle(day: string, time: number)`
2. **Whole Day Selection**: `handleSelectWholeDay(date: Date)`
3. **Drag Selection**: `handleDragStart`, `handleDragOver`, `handleDragEnd`

### 3. Backend Synchronization

#### Data Fetching Flow
```
WeekCalendar → fetchUserAvailabilityFromAPI() → /api/availability/get/[event_id]/[tele_id] → AvailabilityService.getUserAvailability() → Supabase → availability_blocks table
```

#### Data Saving Flow
```
WeekCalendar → updateUserAvailabilityToAPI() → /api/availability/save → AvailabilityService.updateUserAvailability() → Supabase → availability_blocks table
```

#### Throttled Updates
- Uses 2-second debounce to reduce API calls
- `pendingSync` state tracks unsaved changes
- `syncTimeoutRef` manages the debounce timer

### 4. Database Schema

#### availability_blocks Table
```sql
CREATE TABLE availability_blocks (
  event_id        UUID      NOT NULL REFERENCES events(event_id),
  user_uuid       UUID      NOT NULL REFERENCES users(uuid),
  start_time      TIMESTAMPTZ NOT NULL,
  end_time        TIMESTAMPTZ NOT NULL,
  PRIMARY KEY (event_id, user_uuid, start_time)
);
```

#### Data Conversion
**Frontend → Backend**:
- Converts `Set<string>` of UTC ISO datetimes to `AvailabilityData[]`
- Groups consecutive 30-minute slots into time blocks
- Each block represents a continuous time period

**Backend → Frontend**:
- Receives `AvailabilityData[]` with start/end times
- **CRITICAL**: Normalizes all datetime strings to UTC `.000Z` format using `Date.toISOString()`
- Converts to individual 30-minute slots
- Ensures consistent timezone handling

### 5. Timezone Handling (UTC Standardized)

#### Key Functions in `datetime-utils.ts`
```typescript
// Creates date in local timezone, then converts to UTC ISO string
export function getUtcDatetime(day: string, timeMinutes: number): string {
  const [year, month, date] = day.split("-").map(Number);
  const hours = Math.floor(timeMinutes / 60);
  const minutes = timeMinutes % 60;
  
  // Create date in user's local timezone, then convert to UTC
  const localDate = new Date(year, month - 1, date, hours, minutes);
  return localDate.toISOString(); // Always returns UTC with .000Z
}

// Extracts local day and time from UTC ISO string
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

// Simplified slot selection check (no more dual format handling)
export function isSlotSelected(
  dayKey: string, 
  time: number, 
  selectedSlots: Set<string>
): boolean {
  const utcDatetime = getUtcDatetime(dayKey, time);
  return selectedSlots.has(utcDatetime);
}
```

#### Timezone Strategy
- **Storage**: All times stored as UTC ISO strings with `.000Z` format
- **Display**: Times converted to user's local timezone for display
- **Consistency**: No more mixed formats (removed `+00:00` vs `.000Z` issues)
- **User Experience**: Users select times in their local timezone, system converts to UTC

## User Interaction Flow

### 1. Initial Load
1. **Page Load**: `DragSelectorPage` component initializes
2. **URL Parsing**: Extracts `event_id`, `username`, `tele_id` from URL parameters
3. **User Data Fetch**: Gets user UUID from Telegram ID or username
4. **Event Data Fetch**: Retrieves event details and date range
5. **Availability Load**: Fetches existing availability from backend
6. **State Population**: Converts backend data to frontend selection state using normalized UTC format

### 2. Selection Operations

#### Individual Slot Selection
```
User clicks TimeSlot → handleTapToToggle() → updateSelection() → setSelectedSlots() → markPendingSync() → debounced backend update
```

#### Whole Day Selection
```
User clicks DayHeader → handleSelectWholeDay() → iterate through timeSlots → add/remove all slots using getUtcDatetime() → markPendingSync() → debounced backend update
```

#### Drag Selection
```
Mouse down → handleDragStart() → set drag operation (select/deselect)
Mouse move → handleDragOver() → updateSelection() for each slot
Mouse up → handleDragEnd() → markPendingSync() → debounced backend update
```

### 3. Visual Feedback
- **Selected Slots**: Display with primary color and solid variant
- **Dragging State**: Selected slots scale down slightly during drag
- **Disabled Slots**: Grayed out for dates after event end date
- **Loading State**: Spinner overlay during backend operations

## Data Transformation Examples

### Example 1: Frontend Selection to Backend Format
```typescript
// Frontend selection (Set<string>) - all UTC .000Z format
const selectedSlots = new Set([
  "2024-01-15T06:30:00.000Z",  // 2:30 PM local (Singapore +8)
  "2024-01-15T07:00:00.000Z",  // 3:00 PM local
  "2024-01-15T07:30:00.000Z",  // 3:30 PM local
  "2024-01-16T01:00:00.000Z"   // 9:00 AM local
]);

// Backend format (AvailabilityData[])
const availabilityData = [
  {
    user_uuid: "user-123",
    event_id: "event-456",
    start_time: "2024-01-15T06:30:00.000Z",
    end_time: "2024-01-15T08:00:00.000Z"  // 1.5 hour block
  },
  {
    user_uuid: "user-123",
    event_id: "event-456",
    start_time: "2024-01-16T01:00:00.000Z",
    end_time: "2024-01-16T01:30:00.000Z"  // 30 minute block
  }
];
```

### Example 2: Backend Data to Frontend Selection
```typescript
// Backend data (potentially mixed formats from database)
const backendData = [
  {
    start_time: "2024-01-15T06:30:00+00:00",  // May come as timezone offset
    end_time: "2024-01-15T08:00:00+00:00"
  }
];

// Frontend conversion (FIXED: Now normalizes format)
const newSelectedSlots = new Set<string>();
const startDate = new Date("2024-01-15T06:30:00+00:00");
const endDate = new Date("2024-01-15T08:00:00+00:00");

// CRITICAL FIX: Use .toISOString() to normalize format
newSelectedSlots.add(startDate.toISOString()); // "2024-01-15T06:30:00.000Z"

let currentTime = new Date(startDate);
currentTime.setMinutes(currentTime.getMinutes() + 30);

while (currentTime < endDate) {
  const timeString = currentTime.toISOString(); // Always .000Z format
  newSelectedSlots.add(timeString);
  currentTime.setMinutes(currentTime.getMinutes() + 30);
}

// Result: Set with 3 slots, all in consistent .000Z format
// ["2024-01-15T06:30:00.000Z", "2024-01-15T07:00:00.000Z", "2024-01-15T07:30:00.000Z"]
```

## Key Dependencies

### 1. Date-fns Library
- `format()`: Date formatting for display
- `addDays()`: Date arithmetic for navigation
- `parse()`: Date parsing from strings

### 2. NextUI Components
- `Chip`: Visual representation of time slots
- `Button`: Navigation and interaction elements

### 3. Custom Hooks
- `useTelegramViewport`: Telegram Web App viewport management

## Performance Considerations

### 1. Debounced Backend Updates
- 2-second delay prevents excessive API calls
- Only syncs when `syncedWithBackend` is true (after initial load)

### 2. Efficient State Updates
- Uses `Set<string>` for O(1) lookup performance
- **FIXED**: Removed `selectedSlots` from `useCallback` dependencies to prevent infinite re-renders
- Minimal re-renders through proper dependency arrays

### 3. Memory Management
- Cleans up timeouts and event listeners
- Prevents memory leaks in useEffect cleanup functions

## Error Handling

### 1. Data Validation
- Validates date strings before processing
- Handles malformed ISO datetime strings
- Graceful fallbacks for invalid data
- **NEW**: Normalizes all datetime formats to consistent UTC .000Z format

### 2. Network Error Handling
- Try-catch blocks around API calls
- Console logging for debugging
- Graceful degradation when backend is unavailable

### 3. User Feedback
- Loading states during operations
- Error messages for failed operations
- Visual feedback for successful operations

## Debugging and Logging

### 1. Console Logging
- **UPDATED**: Reduced console logging for production performance
- Debug information for selection state changes
- API call tracking and response logging

### 2. Development Tools
- React DevTools for state inspection
- Network tab for API call monitoring
- Console for real-time debugging

## Recent Fixes (UTC Standardization)

### 1. Mixed Format Issue Resolution
- **Problem**: `selectedSlots` contained mixed formats (`+00:00` vs `.000Z`)
- **Solution**: All backend data normalized using `Date.toISOString()`
- **Impact**: Consistent selection detection, no more odd/even day bugs

### 2. Infinite Re-render Fix
- **Problem**: `handleSelectWholeDay` had `selectedSlots` in dependency array
- **Solution**: Removed from dependencies, use functional state updates
- **Impact**: Stable day header selection, no performance issues

### 3. Timezone Conversion Clarity
- **Before**: Complex `normalizeIsoDatetime()` function with bugs
- **After**: Simple `getLocalDayAndTime()` with clear local timezone extraction
- **Impact**: Accurate day detection across all timezones

This architecture now provides a robust, performant, and bug-free time selection system that handles timezone conversions consistently, maintains UTC storage standards, and provides intuitive user interactions across all supported timezones. 