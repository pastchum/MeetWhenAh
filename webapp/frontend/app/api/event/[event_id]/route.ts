import { NextResponse } from 'next/server';
import { getEntry } from '@/app/utils/db_utils';

export async function GET(request: Request, { params }: { params: { event_id: string } }) {
  const eventData = await getEntry('events', 'event_id', params.event_id);

  if (!eventData) {
    return NextResponse.json({ status: 'error', message: 'Event not found' });
  }

  return NextResponse.json({ status: 'success', data: eventData });
}
