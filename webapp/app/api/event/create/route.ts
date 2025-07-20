import { NextRequest, NextResponse } from 'next/server';
import { EventService } from '@/utils/event_service';

const eventService = new EventService();

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { name, description, start_date, end_date, creator_tele_id } = body;
    
    const eventId = await eventService.createEvent(name, description, start_date, end_date, creator_tele_id);
    
    if (eventId) {
      return NextResponse.json({
        status: 'success',
        message: 'Event created successfully',
        data: { event_id: eventId }
      });
    } else {
      return NextResponse.json({
        status: 'error',
        message: 'Failed to create event'
      }, { status: 400 });
    }
  } catch (error) {
    console.error('Error creating event:', error);
    return NextResponse.json({ status: 'error', message: 'Failed to create event' }, { status: 500 });
  }
} 