import { NextRequest, NextResponse } from 'next/server';
import { NewUserData, UserService } from '@/utils/user_service';

const userService = new UserService();

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { tele_user, tele_id } = body;
    const newUserData: NewUserData = {
      tele_id: tele_id,
      tele_user: tele_user,
    };
    const success = await userService.setUser(newUserData);
    
    if (success) {
      const user = await userService.getUser(tele_id);
      return NextResponse.json({
        status: 'success',
        message: 'User added successfully',
        data: user
      });
    } else {
      return NextResponse.json({
        status: 'error',
        message: 'Failed to add user'
      }, { status: 400 });
    }
  } catch (error) {
    console.error('Error adding user:', error);
    return NextResponse.json({ status: 'error', message: 'Failed to add user' }, { status: 500 });
  }
}