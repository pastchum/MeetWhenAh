CREATE TABLE Users (
  tele_user            VARCHAR(255)        PRIMARY KEY,    -- unique user identifier
  sleep_start          VARCHAR(255)        NOT NULL,       -- e.g. "22:30"
  sleep_end            VARCHAR(255)        NOT NULL,       -- e.g. "06:30"
  temp_sleep_start     VARCHAR(255)        NULL,           -- temporary override of sleep_start
  initialised          BOOLEAN     NOT NULL  DEFAULT FALSE,
  callout_cleared      BOOLEAN     NOT NULL  DEFAULT FALSE,
  global_availability  VARCHAR(255)[]      NOT NULL  DEFAULT '{}'  -- e.g. ['Mon09:00-12:00','Wed14:00-18:00']
);

CREATE TABLE Events (
  event_id         VARCHAR(255)      PRIMARY KEY,            -- unique event identifier
  hours_available  VARCHAR(255)[]    NOT NULL  DEFAULT '{}', -- e.g. ['09:00-10:00','15:00-17:00']
  members          VARCHAR(255)[]    NOT NULL  DEFAULT '{}'  -- list of tele_user IDs participating
);