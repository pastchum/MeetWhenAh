import { NextRequest, NextResponse } from 'next/server';
import { AvailabilityService } from '@/utils/availability_service';

const availabilityService = new AvailabilityService();

export async function GET(
  request: NextRequest,
  context: { params: Promise<{ event_id: string }> }
) {
  try {
    const { event_id } = await context.params;
    const eventAvailability = await availabilityService.getEventAvailability(event_id);
    return NextResponse.json({ status: 'success', data: eventAvailability });
  } catch (error) {
    console.error('Error getting event availability:', error);
    return NextResponse.json({ status: 'error', message: 'Failed to get event availability' }, { status: 500 });
  }
} 