export default interface User {
  uuid: string;
  tele_id: string;
  tele_user: string;
  tele_name: string;
  created_at: string;
  updated_at: string;
  initialised: boolean;
  callout_cleared: boolean;
  sleep_start_time: string | null;
  sleep_end_time: string | null;
}