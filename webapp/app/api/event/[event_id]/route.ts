import { NextResponse } from 'next/server';
import { PythonBridge } from '@/lib/python-bridge';

const pythonBridge = new PythonBridge();

export async function GET(request: Request, { params }: { params: Promise<{ event_id: string }> }) {
  try {
    const { event_id } = await params;
    const eventData = await pythonBridge.getEvent(event_id);

    if (!eventData) {
      return NextResponse.json({ status: 'error', message: 'Event not found' });
    }

    return NextResponse.json({ status: 'success', data: eventData });
  } catch (error) {
    console.error('Error getting event:', error);
    return NextResponse.json({ status: 'error', message: 'Failed to get event' }, { status: 500 });
  }
}
