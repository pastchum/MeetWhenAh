import { NextRequest, NextResponse } from 'next/server';
import { PythonBridge } from '@/lib/python-bridge';

const pythonBridge = new PythonBridge();

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { tele_id, sleep_start, sleep_end } = body;
    
    const success = await pythonBridge.setUserSleepPreferences(tele_id, sleep_start, sleep_end);
    
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