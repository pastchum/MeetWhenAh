--DROP table users cascade; DROP TABLE events cascade; DROP TABLE blocked_timings; DROP table membership;

-- 0) Define the enum
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'timing') THEN
        CREATE TYPE timing AS ENUM (
          'MORNING',
          'AFTERNOON',
          'NIGHT'
        );
    END IF;
END $$;


-- 1) Users
CREATE TABLE users (
  uuid           UUID            PRIMARY KEY,
  tele_id        VARCHAR(64) unique,                  -- Telegram numeric ID (if any)
  tele_user      VARCHAR(255) unique,     -- Telegram username
  created_at      TIMESTAMPTZ       NOT NULL DEFAULT NOW(),
  updated_at      TIMESTAMPTZ       NOT NULL DEFAULT NOW(),
  initialised    boolean DEFAULT false,
  callout_cleared      boolean DEFAULT false,
  sleep_start_time     TIMETZ,
  sleep_end_time       TIMETZ,
  tmp_sleep_start      TIMETZ                      -- temporary override
);

-- 2) Events
CREATE TABLE events (
  event_id        UUID            PRIMARY KEY,
    event_name      VARCHAR(255)    NOT NULL,
    event_description VARCHAR(255)    NOT NULL,    
    event_type      VARCHAR(255)    NOT NULL,
  start_date      TIMESTAMPTZ       NOT NULL,      
  end_date        TIMESTAMPTZ       NOT NULL,      
  start_hour     TIMETZ         NOT NULL DEFAULT '00:00:00.000000+08:00',
  end_hour       TIMETZ         NOT NULL DEFAULT '23:30:00.000000+08:00',
  min_participants INT NOT NULL DEFAULT 2,
  min_duration INT NOT NULL DEFAULT 2, -- in terms of blocks
  max_duration INT NOT NULL DEFAULT 4, -- in terms of blocks
  creator         UUID            NOT NULL
                    REFERENCES users(uuid)
                    ON DELETE RESTRICT,
  created_at      TIMESTAMPTZ       NOT NULL DEFAULT NOW()
);

-- 2.1) Event Confirmations
CREATE TABLE event_confirmations (
  event_id        UUID            NOT NULL
                    REFERENCES events(event_id)
                    ON DELETE CASCADE,
  confirmed_at      TIMESTAMPTZ       NOT NULL DEFAULT NOW(),
  confirmed_start_time TIMESTAMPTZ,
  confirmed_end_time TIMESTAMPTZ,
  PRIMARY KEY (event_id)
);

-- 2.2) Event Chats
CREATE TABLE event_chats (
  event_id        UUID            NOT NULL
                    REFERENCES events(event_id)
                    ON DELETE CASCADE,
  chat_id         BIGINT          NOT NULL,
  thread_id       BIGINT,
  is_reminders_enabled BOOLEAN NOT NULL DEFAULT false,
  PRIMARY KEY (event_id, chat_id)
);

-- 2.3) Event Reminders
CREATE TABLE event_reminders (
  event_id        UUID            NOT NULL
                    REFERENCES events(event_id)
                    ON DELETE CASCADE,
  chat_id         BIGINT          NOT NULL,
  thread_id     BIGINT,
  job_id   VARCHAR(255)       NOT NULL,
  PRIMARY KEY (event_id, chat_id)
);

-- 3) Membership
CREATE TABLE membership (
  user_uuid       UUID      NOT NULL
                    REFERENCES users(uuid)
                    ON DELETE CASCADE,
  event_id        UUID      NOT NULL
                    REFERENCES events(event_id)
                    ON DELETE CASCADE,
  joined_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  emoji_icon      TEXT   NOT NULL,
  PRIMARY KEY (user_uuid, event_id)
);

-- 4) Availability blocks
CREATE TABLE availability_blocks (
  event_id        UUID      NOT NULL
                    REFERENCES events(event_id)
                    ON DELETE CASCADE,
  user_uuid       UUID      NOT NULL
                    REFERENCES users(uuid)
                    ON DELETE CASCADE,
  start_time    TIMESTAMPTZ       NOT NULL,      
  end_time      TIMESTAMPTZ       NOT NULL,      
  PRIMARY KEY (event_id, user_uuid, start_time)
);

-- 5) Blocked Timings
CREATE TABLE blocked_timings (
    uuid          UUID            NOT NULL
                    REFERENCES users(uuid)
                        ON DELETE CASCADE,
    start_time          TIMESTAMPTZ            NOT NULL,
    end_time            TIMESTAMPTZ            NOT NULL,
    PRIMARY KEY (uuid, start_time, end_time)
);

-- indexes
CREATE INDEX IF NOT EXISTS idx_events_creator ON events (creator);
CREATE INDEX IF NOT EXISTS idx_membership_event_id ON membership (event_id);
CREATE INDEX IF NOT EXISTS idx_membership_user_uuid ON membership (user_uuid);
CREATE INDEX IF NOT EXISTS idx_availability_blocks_event_id ON availability_blocks (event_id);
CREATE INDEX IF NOT EXISTS idx_availability_blocks_user_uuid ON availability_blocks (user_uuid);
CREATE INDEX IF NOT EXISTS idx_availability_blocks_start_time ON availability_blocks (start_time);
CREATE INDEX IF NOT EXISTS idx_blocked_timings_uuid ON blocked_timings (uuid);