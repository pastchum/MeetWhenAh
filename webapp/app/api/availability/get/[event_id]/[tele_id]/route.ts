import { NextRequest, NextResponse } from 'next/server';
import { getUserAvailability } from '@/utils/availability_utils';

export async function GET(
  request: NextRequest,
  context: { params: Promise<{ event_id: string; tele_id: string }> }
) {
  const { event_id, tele_id } = await context.params;
  const availability = await getUserAvailability(tele_id, event_id);
  console.log("availability", availability);
  return NextResponse.json({ status: 'success', data: availability });
}
