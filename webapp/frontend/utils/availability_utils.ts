import { supabase, TableRow } from '@/lib/db' ;
import { getUserDataFromId } from './user_utils';

export interface AvailabilityData {
    user_uuid: string;
    event_id: string;
    start_time: string;
    end_time: string;
}

export async function getUserAvailability(tele_id: string, event_id: string) {
  const user = await getUserDataFromId(tele_id);
  if (!user) {
    console.error('User not found');
    return null;
  }
  const user_uuid = user.uuid;
  const { data, error } = await supabase
    .from('availability_blocks')
    .select('*')
    .eq('user_uuid', user_uuid)
    .eq('event_id', event_id);

  if (error) {
    console.error('Error fetching availability:', error);
    return null;
  }

  return data;
}

export async function updateUserAvailability(tele_id: string, event_id: string, availability_data: any) {
    const user = await getUserDataFromId(tele_id);
    if (!user) {
        console.error('User not found');
        return false;
    }
    const user_uuid = user.uuid;
    const { error: deleteError } = await supabase
        .from('availability_blocks')
        .delete()
        .eq('user_uuid', user_uuid)
        .eq('event_id', event_id);

    if (deleteError) {
        console.error('Error deleting availability:', deleteError);
        return false;
    }

    const { data: data, error: insertError } = await supabase
        .from('availability_blocks')
        .insert(availability_data);

    if (insertError) {
        console.error('Error inserting availability:', insertError);
        return false;
    }

    return true;
}
