import { NextRequest, NextResponse } from 'next/server';
import { updateUserAvailability } from '@/utils/availability_utils';

export async function POST(request: NextRequest) {
  const body = await request.json();
  const { tele_id, event_id, availability_data } = body;

  const success = await updateUserAvailability(tele_id, event_id, availability_data);

  return NextResponse.json(
    success
      ? { status: 'success', message: 'Availability updated successfully' }
      : { status: 'error', message: 'Failed to update availability' }
  );
}
