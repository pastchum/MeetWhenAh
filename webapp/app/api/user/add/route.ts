import { NextRequest, NextResponse } from 'next/server';
import { UserService } from '@/utils/user_service';

const userService = new UserService();

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { username, tele_id } = body;
    
    const success = await userService.setUser(tele_id, username);
    
    if (success) {
      return NextResponse.json({
        status: 'success',
        message: 'User added successfully'
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