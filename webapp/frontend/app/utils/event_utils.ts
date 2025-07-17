import { supabase, TableRow } from '@/app/lib/db';

export async function getEvent(event_id: string) {
  const { data, error } = await supabase
    .from('events')
    .select('*')
    .eq('event_id', event_id);
    
    if (error) {
        console.error('Error fetching event:', error);
        return null;
    }

    return data;
}

