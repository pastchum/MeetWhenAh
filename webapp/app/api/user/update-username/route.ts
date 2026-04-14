import { NextRequest, NextResponse } from 'next/server';
import { UserService } from '@/utils/user_service';

const userService = new UserService();

export async function POST(request: NextRequest) {
    try {
        const body = await request.json();
        const { tele_id, tele_user } = body;
        const success = await userService.updateUsername(tele_id, tele_user);

        if (!success) {
            return NextResponse.json({ status: 'error', message: 'Failed to update username' }, { status: 400 });
        }

        const user = await userService.getUser(tele_id);
        return NextResponse.json({ status: 'success', data: user });
    } catch (error) {
        console.error('Error updating username:', error);
        return NextResponse.json({ status: 'error', message: 'Failed to update username' }, { status: 500 });
    }
}