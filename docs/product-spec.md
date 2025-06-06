# Meet When Ah? Product Specification

## 1. Overview and Objectives

The **Meet When Ah?** bot will continue to help organizers and participants find the best meeting slot across multiple days and times—but we want to:

1. **Improve the "best time block" algorithm** to:
    - Better handle "sleep hours" (e.g., exclude or penalize 1:00 AM to 6:00 AM).
    - More robustly identify the largest contiguous block of availability among all participants.

2. **Enhance the front-end**:
    - Users should be able to indicate availability in half-hour (or hour) blocks via an inline web app within Telegram (with minimal friction).
    - Because "dragging" to select time might not be ideal on mobile, explore an alternate design that's still easy: e.g., tap-to-toggle each block.
    - Provide fallback for when the inline web app is too cramped on Telegram mobile, by allowing a redirect to a standalone website.

3. **Enable two main flows**:
    - **Flow One**: The existing approach. Organizer sets a date range and invites participants to mark availability. The best time block is auto-calculated once everyone has responded.
    - **Flow Two**: A simplified "polling" approach. Organizer directly picks specific dates/times. The bot posts them in chat. Participants quickly pick which ones they can join. Then the bot:
        - Tracks who said "yes" to each proposed slot.
        - Sends participants reminders (1 day, 1 hour, and 30 minutes before start time).

4. **Extend Reminders**:
    - For any finalized time slot, the bot automatically DMs participants with reminders at specified intervals.

## 2. User Stories

### 2.1 Organizer Stories

1. **As an Organizer**  
    _I want to create a new event within my group chat,_  
    so that _I can poll the group for availability_.

2. **As an Organizer**  
    _I want to specify either (A) a date range or (B) discrete candidate dates/times,_  
    so that _the group can respond in whichever method suits us best_.

3. **As an Organizer**  
    _I want to see which times have the highest overlap in availability,_  
    so that _I can choose the best meeting slot quickly without manually comparing data_.

4. **As an Organizer**  
    _I want to automatically remind participants of the event time after it's decided,_  
    so that _I don't have to chase them manually_.

### 2.2 Participant Stories

1. **As a Participant**  
    _I want a simple interface (on web) to mark my availability on each day/time slot,_  
    so that _I can share my free times quickly and accurately_.

2. **As a Participant**  
    _I want to be able to quickly confirm or decline attendance for a few proposed date/time options,_  
    so that _I don't need to do complicated selection—just a quick poll-like interface_.

3. **As a Participant**  
    _I want to receive reminders 1 day, 1 hour, and 30 minutes before the event,_  
    so that _I won't forget it once it's scheduled_.

### 2.3 UX / Front-End Stories

1. **As a Mobile User**  
    _I want an easy way (tap-based or minimal drag) to indicate my availability,_  
    so that _I don't accidentally scroll or lose my place while selecting time blocks_.

2. ~~**As a Mobile User**~~  
    ~~_I want an option to open a dedicated website (outside Telegram) if the inline view is too small,_~~  
    ~~so that _I can have a better, bigger selection screen_.~~

## 3. Features & Requirements

### 3.1 Best Time Block Algorithm

- **Algorithm**
    - Must consider user-defined "sleep hours" (e.g., `00:00–06:00`) as generally unavailable or very low priority.
    - Must identify the largest contiguous block or the block with the maximum unique participants. If multiple blocks tie, it can pick the earliest.
    - Must handle partial overlaps gracefully—if some participants only overlap half a block, weight that accordingly (or just filter down to blocks where the same group is fully available).

- **Configuration**
    - Possibly let each user set their own "sleep hours" in a personal config, or set a universal default (e.g., 1:00 AM–6:00 AM).
    - The algorithm should skip those hours in the final calculation.

### 3.2 Enhanced Availability Selection (Front End)

- **Inline Web App**
    - Implement a grid or a calendar-like interface. Each date is broken down into half-hour or hour slots.
    - Instead of purely "dragging," consider a _tap-to-toggle_ approach:
        1. User taps once on a time slot to mark it "Available."
        2. Tap again to unmark.
    - Provide smooth scrolling or arrow-based date navigation to minimize accidental swipes.

- **Standalone Web App**
    - Same UI as inline mode, but hosted in a browser window.
    - If the user is on a mobile device, let them "Open in Browser" for a bigger view.
    - The results (selected times) are posted back to the bot via the usual WebApp data flow.

### 3.3 Two Flows

#### Flow One: Range-based Scheduling

1. **Organizer** sends `/createevent <event_name>` in a private chat or group chat with the bot.
    1. Private chat: Means we can send it out to multiple GCs through the link
    2. **Group Chat: More organized, restrict just to one group.**
2. The web app prompts: "Pick a date range for your event."
3. The WebApp collects the start/end date.
4. Set a **CUTOFF TIME** to reply.
5. The Bot generates a shareable link or inline query. (not required if we are inside the gc)
6. The group sees "**[Event Name]**: Click to join and submit your availability."
7. Participants open the availability selection (web).
8. **After** cut-off time, the Bot runs the improved best-time calculation.
9. Organizer (original sender) opens the web app and picks the best timing for the meeting.
10. The bot auto creates reminders in the GROUP CHAT

#### Flow Two: Discrete Date Polling

1. **Organizer** uses `/createpoll <event_name>` in a private chat or group chat.
2. The Bot prompts: "List all candidate date/time slots. Example: `YYYY-MM-DD hh:mm`."
3. The Bot displays them in a poll-like message in the group:
    - "Option A: Monday 3 PM"
    - "Option B: Tuesday 11 AM"
    - "Option C: Wednesday 2 PM"
4. Participants click "I can attend" or "I cannot attend" for each discrete option.
5. The Bot tracks how many yes's each option gets.
6. The Organizer picks the winning option (or the bot automatically chooses the top choice if the poll is set to auto-close).
7. The Bot sets reminders 1 day, 1 hour, 30 min prior.

### 3.5 Commands & Parameters

1. **`/create_event <event_name>`** (Flow One)
    - Send command inside group chat with the bot.
    - Front end page gets opened up
        - If no group has been created yet, create group
    - The bot will prompt for name, date range
    - Once done, the bot shares the "Click to Join" message in the group.
    2. Click to join flow
        - Group member joins the group if they haven't
        - Select the timings they are available (should be global so should have their past availability too) they can continue to edit
        - There should be a button to click to join event (The webapp should have a list of events we can join in the group)

2. **`/create_poll <event_name>`** (Flow Two)
    - The bot asks the organizer for discrete date/time slots (like "YYYY-MM-DD HH:MM"), possibly multiple lines.
    - Then it posts a poll-style message in the group.

3. **`/choose <poll_option>`**
    - (Optional) If the poll is not automated, the Organizer can confirm which option wins.

4. **`/reminders`**
    - (Optional) Let the organizer adjust reminder times or turn them off.
    - Example: `/reminders off` or `/reminders 24h 30m`.

## 4. Technical Approach

1. **Database**
    - Supabase
    - Store user docs, event docs, availability data, poll data.
    - For Flow Two, store a list of discrete times with a list of user IDs who voted "yes."

2. **Improved Scheduling Algorithm**
    - For Flow One:
        1. Gather all user availability per half-hour.
        2. Filter the user's "sleep hours."
        3. Identify the maximum group overlap block.
        4. If multiple tie, pick earliest or the one with the biggest block length.

3. **Reminder Scheduling**
    - Possibly store the chosen event time in Firestore.
    - Use a background task or external scheduler (e.g., cron job or APScheduler) that checks for events starting soon.
    - Send Telegram messages at the intervals specified (24h, 1h, 30min).

4. **UX for Mobile**
    - Inline approach with a day-by-day scroll or pagination, each half-hour slot toggling on tap.
    - A dedicated link "Open in Browser" for easier large-screen usage.

## 5. Acceptance Criteria

1. **Improved Algorithm**
    - The best time calculation must exclude (or significantly penalize) typical sleep hours.
    - Must handle ties deterministically.

2. **Availability Selection**
    - Users can toggle each time slot on/off.
    - On mobile, no accidental scroll that disrupts selection.
    - A fallback website with the same functionality.

3. **Flow One**
    - Organizer can finalize event time after all have responded.
    - The final inline message updates to show the chosen date/time.

4. **Flow Two**
    - The group sees a poll with discrete date/time options.
    - The organizer or the bot finalizes a single date/time.
    - The bot schedules reminders automatically for each user who clicked "Yes."

5. **Reminders**
    - Each participant receives a Telegram direct message at 24h, 1h, 30min intervals (unless turned off).
    - Must handle participants who joined after the event creation or who left.

6. **Commands**
    - `/createevent <name>` & `/createpoll <name>` tested, working.
    - Users can always call `/start` to re-init if something breaks.

7. **Performance**
    - Must handle up to a moderate group size (e.g., 50–100 participants) without timeouts.

## 6. Conclusion

Implementing these requirements will build on your existing system, adding a second scheduling flow and refining your front-end availability selection. By carefully thinking through mobile UX, ensuring the best-time algorithm is robust, and adding reminders, we'll deliver a strong next version that meets your needs.

Feel free to refine specific details (especially the exact commands or how the discrete poll data is submitted) to suit your team's preferences and user feedback. 