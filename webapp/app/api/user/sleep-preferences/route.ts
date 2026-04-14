import { NextRequest, NextResponse } from 'next/server';
import { UserService } from '@/utils/user_service';

const userService = new UserService();

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const tele_id = body.tele_id;
    const sleepStart = body.sleep_start_time ?? body.sleep_start;
    const sleepEnd = body.sleep_end_time ?? body.sleep_end;
    
    const success = await userService.setUserSleepPreferences(tele_id, sleepStart, sleepEnd);
    
    if (success) {
      return NextResponse.json({
        status: 'success',
        message: 'Sleep preferences updated successfully'
      });
    } else {
      return NextResponse.json({
        status: 'error',
        message: 'Failed to update sleep preferences'
      }, { status: 400 });
    }
  } catch (error) {
    console.error('Error updating sleep preferences:', error);
    return NextResponse.json({ status: 'error', message: 'Failed to update sleep preferences' }, { status: 500 });
  }
} 