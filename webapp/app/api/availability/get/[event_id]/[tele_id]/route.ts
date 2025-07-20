import { NextRequest, NextResponse } from 'next/server';
import { PythonBridge } from '@/lib/python-bridge';

const pythonBridge = new PythonBridge();

export async function GET(
  request: NextRequest,
  context: { params: Promise<{ event_id: string; tele_id: string }> }
) {
  try {
    const { event_id, tele_id } = await context.params;
    const availability = await pythonBridge.getUserAvailability(tele_id, event_id);
    console.log("availability", availability);
    return NextResponse.json({ status: 'success', data: availability });
  } catch (error) {
    console.error('Error getting availability:', error);
    return NextResponse.json({ status: 'error', message: 'Failed to get availability' }, { status: 500 });
  }
}
