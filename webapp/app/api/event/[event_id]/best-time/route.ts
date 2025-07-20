import { NextResponse } from 'next/server';
import { PythonBridge } from '@/lib/python-bridge';

const pythonBridge = new PythonBridge();

export async function GET(request: Request, { params }: { params: Promise<{ event_id: string }> }) {
  try {
    const { event_id } = await params;
    const bestTime = await pythonBridge.getEventBestTime(event_id);

    if (!bestTime || bestTime.length === 0) {
      return NextResponse.json({ status: 'error', message: 'No best time found for event' });
    }

    return NextResponse.json({ status: 'success', data: bestTime });
  } catch (error) {
    console.error('Error getting event best time:', error);
    return NextResponse.json({ status: 'error', message: 'Failed to get event best time' }, { status: 500 });
  }
} 