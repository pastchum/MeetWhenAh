import { NextResponse } from 'next/server';
import { getUserAvailability } from '@/app/utils/availability_utils'; 

export async function GET(request: Request, { params }: { params: { tele_id: string, event_id: string } }) {
  const availability = await getUserAvailability(params.tele_id, params.event_id);
  return NextResponse.json({ status: 'success', data: availability });
}
