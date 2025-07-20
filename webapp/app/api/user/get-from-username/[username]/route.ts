import { NextResponse } from 'next/server';
import { getUserDataFromUsername } from '@/utils/user_utils';

export async function GET(request: Request, { params }: { params: Promise<{ username: string }> }): Promise<NextResponse> {
  const { username } = await params;
  const user = await getUserDataFromUsername(username);

  if (!user) {
    return NextResponse.json({ status: 'error', message: 'User not found' });
  }
  console.log(user);
  return NextResponse.json({
    status: 'success',
    data: {
      uuid: user.uuid,
      tele_user: user.tele_user,
      tele_id: user.tele_id
    }
  });
}
