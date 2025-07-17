import { NextResponse } from 'next/server';
import { getEntry } from '@/app/utils/db_utils';

export async function GET(request: Request, { params }: { params: { username: string } }) {
  const user = await getEntry('users', 'tele_user', params.username);

  if (!user) {
    return NextResponse.json({ status: 'error', message: 'User not found' });
  }

  return NextResponse.json({
    status: 'success',
    data: {
      uuid: user.uuid,
      username: user.username,
      tele_id: user.tele_id
    }
  });
}
