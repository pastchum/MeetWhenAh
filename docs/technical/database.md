# Database Specification

## Overview

The MeetWhenAh database is designed to support a meeting scheduling application that integrates with Telegram. The system manages users, events, availability, and scheduling preferences to facilitate group meeting coordination.

## Database Technology

- **Database**: PostgreSQL via Supabase
- **Timezone Support**: TIMESTAMPTZ for timezone-aware timestamps
- **UUID Primary Keys**: All primary keys use UUID for distributed system compatibility

## Schema Structure

### 1. Custom Types

#### `timing` Enum

```sql
CREATE TYPE timing AS ENUM (
  'MORNING',
  'AFTERNOON',
  'NIGHT'
);
```

- **Purpose**: Defines time-of-day preferences for availability
- **Usage**: Used in the `membership` table to specify when users are available by blocks, for better preferential assignment

### 2. Core Tables

#### `users` Table

**Purpose**: Stores user information and preferences

| Column             | Type         | Constraints             | Description                       |
| ------------------ | ------------ | ----------------------- | --------------------------------- |
| `uuid`             | UUID         | PRIMARY KEY             | Unique user identifier            |
| `tele_id`          | VARCHAR(64)  | UNIQUE                  | Telegram numeric ID               |
| `tele_user`        | VARCHAR(255) | UNIQUE                  | Telegram username                 |
| `created_at`       | TIMESTAMPTZ  | NOT NULL, DEFAULT NOW() | Account creation timestamp        |
| `updated_at`       | TIMESTAMPTZ  | NOT NULL, DEFAULT NOW() | Last update timestamp             |
| `initialised`      | BOOLEAN      | DEFAULT FALSE           | User setup completion flag        |
| `callout_cleared`  | BOOLEAN      | DEFAULT FALSE           | Notification status flag          |
| `sleep_start_time` | TIMETZ       | NULLABLE                | User's sleep schedule start       |
| `sleep_end_time`   | TIMETZ       | NULLABLE                | User's sleep schedule end         |
| `tmp_sleep_start`  | TIMETZ       | NULLABLE                | Temporary sleep schedule override |

**Key Features**:

- Dual Telegram identification (ID and username)
  ID uniquely identifies users while username refers to their telegram handle, updated based on any changes on the user side.
- Sleep schedule management
- User initialization tracking
- Notification management

#### `events` Table

**Purpose**: Defines meeting events and their parameters

| Column              | Type         | Constraints                        | Description              |
| ------------------- | ------------ | ---------------------------------- | ------------------------ |
| `event_id`          | UUID         | PRIMARY KEY                        | Unique event identifier  |
| `event_name`        | VARCHAR(255) | NOT NULL                           | Event title              |
| `event_description` | VARCHAR(255) | NOT NULL                           | Event description        |
| `event_type`        | VARCHAR(255) | NOT NULL                           | Event category/type      |
| `start_date`        | TIMESTAMPTZ  | NOT NULL                           | Event start date/time    |
| `end_date`          | TIMESTAMPTZ  | NOT NULL                           | Event end date/time      |
| `start_hour`        | TIMETZ       | NOT NULL, DEFAULT '00:00:00+08:00' | Daily start time         |
| `end_hour`          | TIMETZ       | NOT NULL, DEFAULT '23:30:00+08:00' | Daily end time           |
| `creator`           | UUID         | NOT NULL, FK to users(uuid)        | Event creator            |
| `created_at`        | TIMESTAMPTZ  | NOT NULL, DEFAULT NOW()            | Event creation timestamp |

**Key Features**:

- Flexible date/time ranges
- Daily time windows for recurring events
- Creator tracking with restricted deletion

#### `membership` Table

**Purpose**: Manages user participation in events

| Column           | Type        | Constraints                                       | Description                 |
| ---------------- | ----------- | ------------------------------------------------- | --------------------------- |
| `user_uuid`      | UUID        | NOT NULL, FK to users(uuid)                       | User identifier             |
| `event_id`       | UUID        | NOT NULL, FK to events(event_id)                  | Event identifier            |
| `joined_at`      | TIMESTAMPTZ | NOT NULL, DEFAULT NOW()                           | Join timestamp              |
| `emoji_icon`     | TEXT        | NOT NULL                                          | User's emoji representation |
| `available_time` | timing[]    | NOT NULL, DEFAULT ['MORNING','AFTERNOON','NIGHT'] | Availability preferences    |

**Primary Key**: (`user_uuid`, `event_id`)

**Key Features**:

- Many-to-many relationship between users and events
- Personal emoji icons for visual identification
- Time-of-day availability preferences
- Cascade deletion when user or event is removed

#### `availability_blocks` Table

**Purpose**: Tracks specific time blocks when users are unavailable

| Column       | Type        | Constraints                      | Description      |
| ------------ | ----------- | -------------------------------- | ---------------- |
| `event_id`   | UUID        | NOT NULL, FK to events(event_id) | Event identifier |
| `user_uuid`  | UUID        | NOT NULL, FK to users(uuid)      | User identifier  |
| `start_time` | TIMESTAMPTZ | NOT NULL                         | Block start time |
| `end_time`   | TIMESTAMPTZ | NOT NULL                         | Block end time   |

**Primary Key**: (`event_id`, `user_uuid`, `start_time`)

**Key Features**:

- Granular availability tracking
- Event-specific blocking
- Cascade deletion with events and users

#### `blocked_timings` Table

**Purpose**: Global date-based blocking for users

| Column         | Type | Constraints                 | Description     |
| -------------- | ---- | --------------------------- | --------------- |
| `uuid`         | UUID | NOT NULL, FK to users(uuid) | User identifier |
| `start_timing` | DATE | NOT NULL                    | Blocked date    |

**Primary Key**: (`uuid`, `start_timing`)

**Key Features**:

- Date-level blocking (entire days)
- Global blocking across all events
- Cascade deletion with user removal

## Relationships

### Entity Relationship Diagram

```
users (1) ←→ (N) membership (N) ←→ (1) events
  ↓                                    ↓
blocked_timings              availability_blocks
```

### Relationship Details

1. **Users ↔ Events** (Many-to-Many via `membership`)

   - Users can participate in multiple events
   - Events can have multiple participants
   - Membership includes availability preferences

2. **Users → Blocked Timings** (One-to-Many)

   - Users can have multiple blocked dates
   - Global blocking affects all events

3. **Events → Availability Blocks** (One-to-Many)

   - Events can have multiple availability blocks
   - Event-specific blocking

4. **Users → Availability Blocks** (One-to-Many)
   - Users can have multiple availability blocks per event

## Indexes

The database includes strategic indexes for performance optimization:

| Index                                | Table               | Columns    | Purpose                         |
| ------------------------------------ | ------------------- | ---------- | ------------------------------- |
| `idx_events_creator`                 | events              | creator    | Fast event creator lookups      |
| `idx_membership_event_id`            | membership          | event_id   | Fast event participant queries  |
| `idx_membership_user_uuid`           | membership          | user_uuid  | Fast user event queries         |
| `idx_availability_blocks_event_id`   | availability_blocks | event_id   | Fast event availability queries |
| `idx_availability_blocks_user_uuid`  | availability_blocks | user_uuid  | Fast user availability queries  |
| `idx_availability_blocks_start_time` | availability_blocks | start_time | Time-based availability queries |
| `idx_blocked_timings_uuid`           | blocked_timings     | uuid       | Fast user blocking queries      |

## Data Integrity

### Foreign Key Constraints

- **Cascade Deletion**: Membership and availability blocks are automatically removed when users or events are deleted
- **Restricted Deletion**: Events cannot be deleted if they have participants (creator reference)

### Unique Constraints

- Telegram ID and username are unique per user
- User-event membership is unique
- Availability blocks are unique per event-user-start_time combination
- Blocked timings are unique per user-date combination

## Timezone Handling

The database uses timezone-aware timestamps (`TIMESTAMPTZ`) throughout:

- All timestamps include timezone information
- Default timezone appears to be UTC+8 (Singapore/Asia)
- Supports users across different timezones

## Use Cases

### 1. Event Creation

1. User creates event in `events` table
2. User automatically becomes member via `membership` table
3. Event has default daily time windows

### 2. User Registration

1. User registers via Telegram integration
2. User record created in `users` table
3. User can set sleep schedule and preferences

### 3. Availability Management

1. Users join events via `membership` table
2. Users set time-of-day preferences (`available_time`)
3. Users can block specific dates (`blocked_timings`)
4. Users can block specific time ranges per event (`availability_blocks`)

### 4. Scheduling Algorithm

The database supports complex scheduling by:

- Checking user availability preferences
- Respecting blocked dates and times
- Considering sleep schedules
- Finding optimal meeting times across all participants

## Scalability Considerations

- **UUID Primary Keys**: Support distributed systems and avoid ID conflicts
- **Strategic Indexing**: Optimized for common query patterns
- **Normalized Design**: Reduces data redundancy
- **Cascade Deletion**: Maintains referential integrity automatically

## Security Features

- **Telegram Integration**: Secure user authentication via Telegram
- **Unique Constraints**: Prevents duplicate registrations
- **Referential Integrity**: Foreign key constraints prevent orphaned data

## Planned extensions

###Confirmed events

- When events are confirmed, the finalised date and time will be stored.
- Reminder frequency stored as well to facilitate reminders.
