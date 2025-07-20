import { NextResponse } from 'next/server';
import { UserService } from '@/utils/user_service';

const userService = new UserService();

export async function GET(request: Request, { params }: { params: Promise<{ username: string }> }): Promise<NextResponse> {
  try {
    const { username } = await params;
    const user = await userService.getUserByUsername(username);

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
  } catch (error) {
    console.error('Error getting user by username:', error);
    return NextResponse.json({ status: 'error', message: 'Failed to get user' }, { status: 500 });
  }
}
