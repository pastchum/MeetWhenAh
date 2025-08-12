import { NextRequest, NextResponse } from 'next/server';
import { EventService } from '@/utils/event_service';

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ tele_id: string }> }
) {
  try {
    const { tele_id } = await params;
    
    if (!tele_id) {
      return NextResponse.json(
        { error: 'Missing tele_id parameter' },
        { status: 400 }
      );
    }

    const eventService = new EventService();
    const events = await eventService.getUserEvents(tele_id);
    
    return NextResponse.json({
      success: true,
      data: events
    });
  } catch (error) {
    console.error('Error getting user events:', error);
    return NextResponse.json(
      { error: 'Failed to get user events' },
      { status: 500 }
    );
  }
} 