import { NextResponse } from 'next/server';
import { getEvent } from '@/utils/event_utils';

export async function GET(request: Request, { params }: { params: Promise<{ event_id: string }> }) {
  const { event_id } = await params;
  const eventData = await getEvent(event_id);

  if (!eventData) {
    return NextResponse.json({ status: 'error', message: 'Event not found' });
  }

  return NextResponse.json({ status: 'success', data: eventData });
}
