import { supabase, TableRow } from '@/lib/db' ;

export async function getUserAvailability(tele_id: string, event_id: string) {
  const { data, error } = await supabase
    .from('availability')
    .select('*')
    .eq('tele_id', tele_id)
    .eq('event_id', event_id);

  if (error) {
    console.error('Error fetching availability:', error);
    return null;
  }

  return data;
}

export async function updateUserAvailability(tele_id: string, event_id: string, availability_data: any) {
    const { error: deleteError } = await supabase
        .from('availability')
        .delete()
        .eq('tele_id', tele_id)
        .eq('event_id', event_id);

    if (deleteError) {
        console.error('Error deleting availability:', deleteError);
        return false;
    }

    const { data: data, error: insertError } = await supabase
        .from('availability')
        .insert(availability_data);

    if (insertError) {
        console.error('Error inserting availability:', insertError);
        return false;
    }

    return true;
}
