# WeekCalendar Data Flow Diagram

## Component Hierarchy and Data Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           DragSelectorPage                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ URL Params: event_id, username, tele_id                            │   │
│  │ State: eventDetails, startDate, endDate, selectionData            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           WeekCalendar                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ Props: startDate, endDate, tele_id, eventId, userUuid             │   │
│  │ State: selectedSlots (Set<string>), isDragging, pendingSync       │   │
│  │                                                                     │   │
│  │ Key Functions:                                                     │   │
│  │ • fetchUserAvailability()                                          │   │
│  │ • syncToBackend()                                                  │   │
│  │ • handleSelectWholeDay()                                           │   │
│  │ • handleDragStart/Over/End()                                       │   │
│  │ • handleTapToToggle()                                              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
        ┌─────────────────┐ ┌─────────────┐ ┌─────────────┐
        │   DayHeader     │ │  TimeColumn │ │   TimeGrid  │
        │                 │ │             │ │             │
        │ • Date display  │ │ • Time      │ │ • Grid      │
        │ • Click to      │ │   labels    │ │   layout    │
        │   select day    │ │ • 30-min    │ │ • Event     │
        │                 │ │   intervals │ │   handling  │
        └─────────────────┘ └─────────────┘ └─────────────┘
                                                      │
                                                      ▼
                                        ┌─────────────────────────┐
                                        │       TimeSlot          │
                                        │                         │
                                        │ • Individual slot       │
                                        │ • Mouse/touch events    │
                                        │ • Visual state          │
                                        │ • Drag operations       │
                                        └─────────────────────────┘
```

## Data Transformation Flow (UTC Standardized)

### 1. Frontend Selection State
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    selectedSlots: Set<string>                              │
│                       (All UTC .000Z format)                               │
│                                                                             │
│  "2024-01-15T06:30:00.000Z"  ← 2:30 PM local (Singapore +8) as UTC        │
│  "2024-01-15T07:00:00.000Z"  ← 3:00 PM local as UTC                       │
│  "2024-01-15T07:30:00.000Z"  ← 3:30 PM local as UTC                       │
│  "2024-01-16T01:00:00.000Z"  ← 9:00 AM local as UTC                       │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼ (syncToBackend)
┌─────────────────────────────────────────────────────────────────────────────┐
│                    availabilityData: AvailabilityData[]                    │
│                                                                             │
│  {                                                                          │
│    user_uuid: "user-123",                                                  │
│    event_id: "event-456",                                                  │
│    start_time: "2024-01-15T06:30:00.000Z",                                │
│    end_time: "2024-01-15T08:00:00.000Z"    ← 1.5 hour block               │
│  },                                                                         │
│  {                                                                          │
│    user_uuid: "user-123",                                                  │
│    event_id: "event-456",                                                  │
│    start_time: "2024-01-16T01:00:00.000Z",                                │
│    end_time: "2024-01-16T01:30:00.000Z"    ← 30 minute block              │
│  }                                                                          │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼ (API POST)
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Supabase: availability_blocks table                     │
│                                                                             │
│  event_id | user_uuid | start_time           | end_time                    │
│  ---------|-----------|----------------------|---------------------------- │
│  event-456| user-123  | 2024-01-15T06:30:00Z | 2024-01-15T08:00:00Z       │
│  event-456| user-123  | 2024-01-16T01:00:00Z | 2024-01-16T01:30:00Z       │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Time Conversion Process

### 1. User Input → UTC ISO String
```
User clicks on "Jan 15, 2:30 PM" (local time)
    │
    ▼
day = "2024-01-15", timeMinutes = 870 (14 * 60 + 30)
    │
    ▼
getUtcDatetime("2024-01-15", 870)
    │
    ▼
new Date(2024, 0, 15, 14, 30).toISOString()  // Local → UTC conversion
    │
    ▼
"2024-01-15T06:30:00.000Z"  // UTC equivalent (Singapore +8)
```

### 2. UTC ISO String → Local Display
```
"2024-01-15T06:30:00.000Z"
    │
    ▼
getLocalDayAndTime(utcString)
    │
    ▼
date = new Date("2024-01-15T06:30:00.000Z")
date.getHours() * 60 + date.getMinutes()  // Local timezone extraction
    │
    ▼
{ day: "2024-01-15", time: 870 }  // 14:30 local time
    │
    ▼
formatTime(870) → "14:30"
```

## Backend Synchronization Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           WeekCalendar                                      │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 1. User makes selection                                             │   │
│  │ 2. setSelectedSlots(newSet) - all UTC .000Z format                 │   │
│  │ 3. setPendingSync(true)                                             │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼ (2-second debounce)
┌─────────────────────────────────────────────────────────────────────────────┐
│                        syncToBackend()                                     │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 1. Convert Set<string> to AvailabilityData[]                       │   │
│  │ 2. Group consecutive UTC slots into time blocks                    │   │
│  │ 3. Call updateUserAvailabilityToAPI()                              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    /api/availability/save                                 │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ POST /api/availability/save                                         │   │
│  │ Body: { tele_id, event_id, availability_data }                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    AvailabilityService.updateUserAvailability()            │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 1. Get user UUID from tele_id                                       │   │
│  │ 2. Delete existing availability blocks                             │   │
│  │ 3. Insert new availability blocks                                  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Supabase Database                                      │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ availability_blocks table                                           │   │
│  │ • event_id (UUID)                                                   │   │
│  │ • user_uuid (UUID)                                                  │   │
│  │ • start_time (TIMESTAMPTZ) - stored as UTC                         │   │
│  │ • end_time (TIMESTAMPTZ) - stored as UTC                           │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

## User Interaction States

### 1. Initial Load State (Fixed Format Handling)
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. Page loads with URL params                                            │
│ 2. Fetch user data (tele_id → user_uuid)                                 │
│ 3. Fetch event data (event_id → event details)                          │
│ 4. Fetch existing availability                                           │
│ 5. FIXED: Convert backend data to frontend using Date.toISOString()     │
│ 6. Render WeekCalendar with populated UTC .000Z format data             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2. Selection State (Simplified)
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ User clicks/drags → TimeSlot events → WeekCalendar handlers              │
│                                                                             │
│ • Individual click: handleTapToToggle()          │
│ • Day header click: handleSelectWholeDay()     │
│ • Drag start: handleDragStart()                                           │
│ • Drag over: handleDragOver()                                             │
│ • Drag end: handleDragEnd()                                               │
│                                                                             │
│ All operations update selectedSlots Set<string> with consistent UTC      │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3. Synchronization State
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ Selection change → pendingSync = true → 2s debounce → API call            │
│                                                                             │
│ • Immediate: Update local state                                           │
│ • 2 seconds: Convert and send to backend                                  │
│ • Success: Clear pendingSync                                              │
│ • Error: Log error, keep pendingSync for retry                           │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Key Utility Functions

### datetime-utils.ts
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Time Conversion Utilities                               │
│                                                                             │
│ getUtcDatetime(day, timeMinutes)                                          │
│ ├─ Input: "2024-01-15", 870 (14:30 local)                                 │
│ └─ Output: "2024-01-15T06:30:00.000Z" (UTC for Singapore +8)              │
│                                                                             │
│ getLocalDayAndTime(utcString)                                             │
│ ├─ Input: "2024-01-15T06:30:00.000Z"                                      │
│ └─ Output: { day: "2024-01-15", time: 870 } (local timezone)              │
│                                                                             │
│ isSlotSelected(dayKey, time, selectedSlots)                               │
│ ├─ Input: "2024-01-15", 870, Set<string>                                  │
│ └─ Output: boolean (consistent UTC comparison)                             │
│                                                                             │
│ REMOVED: normalizeIsoDatetime() - no longer needed                        │
│ REMOVED: getDayAndTimeFromIso() - replaced by getLocalDayAndTime()        │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Recent Fixes Applied

### 1. Mixed DateTime Format Resolution
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ BEFORE: selectedSlots contained mixed formats                            │
│ • "2024-01-15T06:30:00+00:00" (from backend)                              │
│ • "2024-01-15T07:00:00.000Z" (from frontend)                              │
│                                                                             │
│ AFTER: All normalized to .000Z format                                     │
│ • startDate.toISOString() for backend data                                │
│ • currentTime.toISOString() for generated data                            │
│ • Consistent Set<string> lookup and comparison                            │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2. React Re-render Loop Fix
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ BEFORE: useCallback dependency issue                                      │
│ • handleSelectWholeDay had [selectedSlots, ...] in dependencies           │
│ • Every setSelectedSlots() → new function → infinite loop                 │
│                                                                             │
│ AFTER: Clean dependency array                                             │
│ • useCallback([timeSlots, endDate]) - no state dependencies               │
│ • Functional state updates: setSelectedSlots(prev => ...)                 │
│ • Stable function reference, no infinite re-renders                       │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3. Timezone Conversion Clarity
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ BEFORE: Complex timezone handling                                         │
│ • normalizeIsoDatetime() with bug-prone conversion logic                  │
│ • Mixed local/UTC calculations causing day detection issues               │
│                                                                             │
│ AFTER: Simple UTC standard                                                │
│ • getUtcDatetime(): Local input → UTC storage                             │
│ • getLocalDayAndTime(): UTC storage → Local display                       │
│ • Clear separation of concerns, no timezone bugs                          │
└─────────────────────────────────────────────────────────────────────────────┘
```

This diagram shows the complete updated data flow from user interaction through to database storage, highlighting the UTC standardization fixes that resolved the selection detection and infinite re-render issues. 