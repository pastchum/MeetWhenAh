WELCOME_MESSAGE = """
❓ <b>Welcome to Meet When Ah?!</b>

I help you find the best time to meet with your friends. Here's what I can do:

📅 <b>Create events</b> and share them with your friends
⏰ <b>Track everyone's availability</b>
🎯 <b>Find the optimal meeting time</b>
😴 <b>Consider sleep schedules</b> when scheduling

Use /help to see all available commands.
"""

HELP_MESSAGE = """
❓ <b>Available Commands</b>

Here are the commands you can use:

📝 <b>/create</b> - Create a new event
🔗 <b>/share</b> - Share an event with your friends
❓ <b>/help</b> - Show this help message

To create a new event, use the "Create Event" button in our chat.
""" 

REMINDER_ON_MESSAGE = """
✅ <b>Reminders Enabled</b>

Reminders are now on for this event.
"""

REMINDER_OFF_MESSAGE = """
🔕 <b>Reminders Disabled</b>

Reminders are now off for this event.
"""

# Event-related messages
EVENT_CREATED_SUCCESS = """
✅ <b>Event Created Successfully!</b>

{event_description}

Share this event with others using the /share command in your group chats!

Confirm the event here when you're ready!
"""

EVENT_ALREADY_CONFIRMED = """
⚠️ <b>Event Already Confirmed</b>

Event {event_name} is already confirmed.
"""

EVENT_CONFIRMED_SUCCESS = """
✅ <b>Event Confirmed Successfully!</b>

{description}

Share this event with others using the /share command in your group chats!
"""

# Availability and join messages
AVAILABILITY_SELECTION = """
❓ <b>Select Your Availability</b>

{event_description}

Please select your availability for <b>{event_name}</b>:
"""

JOIN_EVENT_PROMPT = """
👥 <b>Join Event</b>

{event_description}

Click the button below to join this event!
"""

# Sleep schedule messages
SLEEP_START_PROMPT = """
😴 <b>Sleep Schedule Setup</b>

Please enter your sleep start time in 24-hour format (HHMM):
For example, 2300 for 11:00 PM
"""

SLEEP_END_PROMPT = """
😴 <b>Sleep Schedule Setup</b>

Now, please enter your sleep end time in 24-hour format (HHMM):
For example, 0700 for 7:00 AM
"""

SLEEP_INVALID_FORMAT = """
❌ <b>Invalid Format</b>

Please enter time in HHMM format (e.g., {example}):
"""

# Share messages
SHARE_EVENT_PROMPT = """
❗️ <b>Event Sharing</b>

Please select an event to share in this chat.
"""

# Group chat messages
GROUP_CREATE_INSTRUCTIONS = """
❓ <b>Private Chat Required</b>

To create an event, please message me privately!
"""

# Test message
BOT_TEST_MESSAGE = """
✅ <b>Bot Status</b>

Bot is working!
"""

# Reminder messages
AVAILABILITY_REMINDER = """
❓ <b>Reminder</b>: Please input your availability for the event

📅 <b>Event</b>: <b>{event_name}</b>
⏰ <b>Possible Dates</b>: {start_date_str} - {end_date_str}
"""

EVENT_REMINDER = """
❗ <b>Reminder</b>: <b>{event_name}</b> is happening soon!

👥 <b>Participants</b>:
{participants}
"""

DAILY_REMINDER = """
❗ <b>Reminder</b>: <b>{event_name}</b> is happening on {start_time_str} to {end_time_str}!

👥 <b>Participants</b>:
{participants}
"""
