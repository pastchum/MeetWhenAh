CREATE OR REPLACE FUNCTION get_unconfirmed_active_events_at_noon_local_time()
RETURNS TABLE (
  event_id UUID,
  event_name VARCHAR,
  timezone VARCHAR,
  local_time TIME
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    e.event_id,
    e.event_name,
    e.timezone,
    (now() AT TIME ZONE 'UTC' AT TIME ZONE e.timezone)::time AS local_time
  FROM events e
  WHERE NOT EXISTS (
    SELECT 1 FROM confirmed_events ce WHERE ce.event_id = e.event_id
  )
  AND e.cancelled = false
  AND e.is_reminders_enabled = true
  AND (now() AT TIME ZONE 'UTC' AT TIME ZONE e.timezone)::time >= '12:00:00'
  AND (now() AT TIME ZONE 'UTC' AT TIME ZONE e.timezone)::time < '12:01:00'
  AND (now() AT TIME ZONE 'UTC' AT TIME ZONE e.timezone)::date <= (e.end_date AT TIME ZONE 'UTC' AT TIME ZONE e.timezone)::date;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION get_confirmed_events_at_local_noon()
RETURNS TABLE (
  event_id UUID,
  event_name VARCHAR,
  timezone VARCHAR,
  confirmed_start_time TIMESTAMPTZ,
  confirmed_end_time TIMESTAMPTZ,
  local_current_time TIME
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    e.event_id,
    e.event_name,
    e.timezone,
    ce.confirmed_start_time,
    ce.confirmed_end_time,
    (now() AT TIME ZONE 'UTC' AT TIME ZONE e.timezone)::time AS local_current_time
  FROM events e
  JOIN confirmed_events ce ON ce.event_id = e.event_id
  WHERE e.cancelled = false
    AND e.is_reminders_enabled = true
    AND ce.confirmed_start_time > now()
    AND (now() AT TIME ZONE 'UTC' AT TIME ZONE e.timezone)::time >= '12:00:00'
    AND (now() AT TIME ZONE 'UTC' AT TIME ZONE e.timezone)::time < '12:01:00';
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION get_confirmed_events_starting_soon()
RETURNS TABLE (
  event_id UUID,
  event_name VARCHAR,
  timezone VARCHAR,
  confirmed_start_time TIMESTAMPTZ,
  confirmed_end_time TIMESTAMPTZ,
  local_current_time TIME
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    e.event_id,
    e.event_name,
    e.timezone,
    ce.confirmed_start_time,
    ce.confirmed_end_time,
    (now() AT TIME ZONE 'UTC' AT TIME ZONE e.timezone)::time AS local_current_time
  FROM events e
  JOIN confirmed_events ce ON ce.event_id = e.event_id
  WHERE e.cancelled = false
    AND e.is_reminders_enabled = true
    AND ce.confirmed_start_time BETWEEN now() AND now() + INTERVAL '2 hours';
END;
$$ LANGUAGE plpgsql;
