import { supabase, TableRow } from '@/lib/db';

export interface EventData {
  event_id: string;
  event_name: string;
  event_description: string;    
  event_type: string;
  start_date: string;
  end_date: string;
  start_hour: string;
  end_hour: string;
  creator: string;
  created_at: string;
}

export async function getEvent(event_id: string) {
  const { data, error } = await supabase
    .from('events')
    .select('*')
    .eq('event_id', event_id);
    
    if (error) {
        console.error('Error fetching event:', error);
        return null;
    }
    console.log(data[0]);
    return {
      event_id: data[0].event_id,
      event_name: data[0].event_name,
      event_description: data[0].event_description,
      event_type: data[0].event_type,
      start_date: data[0].start_date,
      end_date: data[0].end_date,
      start_hour: data[0].start_hour,
      end_hour: data[0].end_hour,
      creator: data[0].creator,
      created_at: data[0].created_at
    };
}

