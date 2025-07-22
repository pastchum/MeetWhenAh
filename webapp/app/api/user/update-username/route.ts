import { NextRequest, NextResponse } from 'next/server';
import { UserService } from '@/utils/user_service';

const userService = new UserService();

export async function POST(request: NextRequest) {
    const body = await request.json();
    const { tele_id, tele_user } = body;
    const success = await userService.updateUsername(tele_id, tele_user);
    return NextResponse.json({ success });
}