import { NextResponse } from 'next/server';
import { getUserDataFromId } from '@/utils/user_utils';

export async function GET(request: Request, { params }: { params: Promise<{ tele_id: string }> }): Promise<NextResponse> {
  const { tele_id } = await params;
  const user = await getUserDataFromId(tele_id);

  if (!user) {
    return NextResponse.json({ status: 'error', message: 'User not found' });
  }

  return NextResponse.json({
    status: 'success',
    data: {
      uuid: user.uuid,
      tele_user: user.tele_user,
      tele_id: user.tele_id
    }
  });
}
