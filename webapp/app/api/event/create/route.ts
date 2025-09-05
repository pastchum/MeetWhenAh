import { NextRequest, NextResponse } from 'next/server';
import { EventService } from '@/utils/event_service';

const eventService = new EventService();

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { token, event_id, event_name, event_details, start, end, creator } = body;
    
    console.log('route: ', body);
    const eventIdResult = await eventService.createEvent(token, event_id, event_name, event_details, start, end, creator);
    
    if (eventIdResult) {
      return NextResponse.json({
        status: 'success',
        message: 'Event created successfully',
        data: { event_id: eventIdResult }
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