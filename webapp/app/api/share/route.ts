import { NextRequest, NextResponse } from 'next/server';
import { ShareService } from '@/utils/share_service';

const shareService = new ShareService();

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { token, event_id } = body;

    const ok = await shareService.share_event(token, event_id);
    if (!ok) {
      return NextResponse.json({ status: 'error', message: 'Failed to share event' }, { status: 500 });
    }

    return NextResponse.json({ status: 'success', message: 'Event shared successfully' });
  } catch (error) {
    console.error('Error creating event:', error);
    return NextResponse.json({ status: 'error', message: 'Failed to create event' }, { status: 500 });
  }
} 