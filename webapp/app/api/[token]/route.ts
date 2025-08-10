import { NextRequest, NextResponse } from 'next/server';
import { ShareService } from '@/utils/share_service';

const shareService = new ShareService();

export async function GET(request: NextRequest, { params }: { params: Promise<{ token: string }> }) {
  const { token } = await params;
  console.log('token', token);
  const ctx = await shareService.get_ctx(token);
  if (ctx) {
    return NextResponse.json(ctx);
  } else {
    return NextResponse.json({ error: 'Invalid token' }, { status: 400 });
  }
}