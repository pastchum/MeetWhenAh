import { NextResponse } from 'next/server';
import { getEntry } from '@/utils/db_utils';

export async function GET(request: Request, { params }: { params: { tele_id: string } }) {
  const user = await getEntry('users', 'tele_id', params.tele_id);

  if (!user) {
    return NextResponse.json({ status: 'error', message: 'User not found' });
  }

  return NextResponse.json({
    status: 'success',
    data: {
      uuid: user.uuid,
      username: user.username
    }
  });
}
