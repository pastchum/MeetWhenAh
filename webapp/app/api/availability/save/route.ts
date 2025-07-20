import { NextRequest, NextResponse } from 'next/server';
import { AvailabilityService } from '@/utils/availability_service';

const availabilityService = new AvailabilityService();

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { tele_id, event_id, availability_data } = body;

    const success = await availabilityService.updateUserAvailability(tele_id, event_id, availability_data);

    return NextResponse.json(
      success
        ? { status: 'success', message: 'Availability updated successfully' }
        : { status: 'error', message: 'Failed to update availability' }
    );
  } catch (error) {
    console.error('Error updating availability:', error);
    return NextResponse.json({ status: 'error', message: 'Failed to update availability' }, { status: 500 });
  }
}
