# 📋 **Flow One: Complete Specification**

## **Phase 1: Event Creation**

### **1.1 Initial Setup**
- User opens bot in **private chat**
- Clicks **"Create Event"** button
- Opens **3-step webapp**:
  - **Step 1**: Event details (name, description)
  - **Step 2**: Date range picker
  - **Step 3**: Summary & submit

### **1.2 Event Created**
- Bot creates event in database
- Bot sends **"Event Created"** message in private chat with **2 inline buttons**:
  - **"Share Event"** → Generates group chat share
  - **"Edit Event"** → Opens event management webapp

---

## **Phase 2: Event Sharing & Availability Collection**

### **2.1 Group Chat Sharing**
- Organizer clicks **"Share Event"** → Bot generates shareable message
- **Shared message** posted in group chat contains:
  - Event name, description, date range
  - **"Update Availability"** button (inline webapp)

### **2.2 Availability Updates**
- Members click **"Update Availability"** → Opens drag-select calendar interface
- **Auto opt-in**: First availability update automatically joins user to event
- **Real-time sync**: Changes save automatically to backend
- **Navigation**: 7-day view with Previous/Next buttons for longer events

### **2.3 Organizer Reminders**
- **Daily reminder** to organizer if no responses after 24h
- **Algorithm consideration**: Lower bound = `max(current_date, event_start_date)`
- **No responses detected**: No reminders sent + auto-delete after `event_end_date`

---

## **Phase 3: Organizer Final Selection**

### **3.1 Dual Interface Access**
When organizer clicks shared event → **two options**:
- **"Update My Availability"** (same interface as members)
- **"Make Final Selection"** (algorithm-powered selection view)

### **3.2 Final Selection Interface**
- **Best time suggestions**: Algorithm calculates optimal times
- **Participation warnings**: Shows availability percentage for each slot
- **Manual override**: Organizer can pick any time (with warnings)
- **Confirmation required**: Final selection is immutable

### **3.3 Algorithm Logic**
- **Optimization**: Maximize participant overlap
- **Time constraints**: Respects event date range + current date lower bound
- **Sleep hours consideration**: Configurable preferences
- **Contiguous blocks**: Prioritizes longer uninterrupted periods

---

## **Phase 4: Event Confirmation & Join Flow**

### **4.1 Post-Selection Updates**
- **Shared message updates** with final confirmed time
- **New buttons appear**:
  - **"Join Event"** (for available participants)
  - **"Confirm You're Free"** (for unavailable participants)
  - **"Leave Event"** (for already joined)

### **4.2 Auto-Join Logic**
- **Available participants**: Automatically joined + calendar blocked
- **Unavailable participants**: Can manually "Confirm You're Free"
- **Calendar blocking**: Prevents double-booking for confirmed attendees

### **4.3 Late Participant Handling**
- **After final selection**: Can still update availability 
- **No auto-join**: Must manually request to join
- **Future extension**: "Request to Join" with organizer approval

---

## **Phase 5: Event Management & Modifications**

### **5.1 Organizer Event Management**
Access via **"Edit Event"** button in private chat:
- **Pre-finalization**: Full editing (name, description, date range)
- **Post-finalization**: Delete only
- **Delete confirmation**: Required with participant notification

### **5.2 Participant Management**
- **Join/Leave**: Available until 24h before event
- **Calendar updates**: Real-time blocking/unblocking
- **No reschedule**: Final time is immutable

### **5.3 Change Restrictions**
- **Organizer**: Cannot change final time (delete/recreate only)
- **Participants**: Can leave anytime, cannot change others' availability

---

## **Phase 6: Reminders & Notifications**

### **6.1 Event Reminders**
- **24-hour reminder**: Private DM to all confirmed participants
- **Daily organizer reminders**: Until final selection made
- **Reminder logic**: Only to joined participants

### **6.2 Notification Fallbacks**
- **DM failure**: Graceful degradation (no group chat fallback)
- **Timezone handling**: Stored in database, converted per user
- **Missed reminders**: No retry mechanism (acceptable failure)

---

## **Phase 7: Post-Event Cleanup**

### **7.1 Event Completion**
- **After event time**: Webapp shows "Event is over" message
- **Shared buttons**: Disabled/removed
- **Calendar unblocking**: Automatic for all participants

### **7.2 Database Cleanup**
- **Availability data**: Auto-deleted after event completion
- **Event record**: Maintained for history (configurable retention)
- **Storage optimization**: Regular cleanup of past availability blocks

---

## **Edge Cases & Error Handling**

### **8.1 Abandonment Scenarios**
- **Zero responses**: Auto-delete after end date
- **Organizer abandonment**: Event remains until auto-cleanup
- **Partial responses**: Organizer can still make selection

### **8.2 System Limitations**
- **Timezone**: Handled in database layer
- **Privacy**: Users see only their own availability
- **Capacity**: No maximum participant limit
- **Late updates**: Allowed but no auto-join after finalization

### **8.3 Failure Modes**
- **Webapp unreachable**: Graceful error messages
- **Database errors**: Retry logic with user feedback
- **Bot downtime**: Event state preserved, resumable

---

## **Technical Requirements**

### **9.1 Database Schema**
- **Events**: event_id, name, description, start_date, end_date, creator, final_time, status
- **Availability**: user_uuid, event_id, time_blocks, created_at
- **Participants**: user_uuid, event_id, status (joined/left), joined_at

### **9.2 Algorithm Components**
- **Overlap calculation**: Real-time participant availability intersection
- **Block optimization**: Contiguous time period identification
- **Preference weighting**: Sleep hours, user patterns (future)

### **9.3 Integration Points**
- **Telegram WebApp**: Seamless bot ↔ webapp transitions
- **Supabase**: Real-time sync with RLS security
- **Timezone**: UTC storage, local display conversion

---

## **Future Extensions (Out of Scope)**

- **Group chat creation**: Direct event creation in groups
- **Availability overlay**: See others' calendars
- **Response deadlines**: Automatic cutoff times
- **Late joiner approval**: Organizer permission flow
- **Event templates**: Recurring meeting patterns
- **Integration**: Calendar app sync
- **Analytics**: Meeting pattern insights

---