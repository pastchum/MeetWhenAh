import { NextRequest, NextResponse } from 'next/server';
import { getUserAvailability } from '@/utils/availability_utils';

export async function GET(
  request: NextRequest,
  context: { params: Promise<{ tele_id: string; event_id: string }> }
) {
  const { tele_id, event_id } = await context.params;
  const availability = await getUserAvailability(tele_id, event_id);
  return NextResponse.json({ status: 'success', data: availability });
}
