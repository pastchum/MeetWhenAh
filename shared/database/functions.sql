CREATE OR REPLACE FUNCTION get_unconfirmed_active_events_at_noon_local_time()
RETURNS TABLE (
  event_id UUID,
  event_name TEXT,
  timezone TEXT,
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
  event_name TEXT,
  timezone TEXT,
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
  event_name TEXT,
  timezone TEXT,
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
    AND ce.confirmed_start_time >= now()
    AND ce.confirmed_start_time < now() + INTERVAL '2 hours';
END;
$$ LANGUAGE plpgsql;

create or replace function cleanup_share_tokens()
returns void language sql as $$
  delete from webapp_share_tokens
  where expires_at < now() or used_at is not null;
$$;

-- select cron.schedule('cleanup_share_tokens_hourly', '0 * * * *', $$select cleanup_share_tokens()$$);

create or replace function get_and_use_share_token(p_token text)
returns setof webapp_share_tokens
language plpgsql
as $$
begin
  return query
  update webapp_share_tokens t
     set used_at = now()
   where t.token = p_token
     and t.used_at is null
     and t.expires_at > now()
  returning t.*;
end;
$$;
