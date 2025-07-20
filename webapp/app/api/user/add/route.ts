import { NextRequest, NextResponse } from 'next/server';
//import { addUser } from '@/utils/user_utils';

export async function POST(request: NextRequest) {
  const body = await request.json();
  //const { username, tele_id } = body;
  //const user = await addUser(username, tele_id);
  return NextResponse.json({
    status: 'success',
    message: 'User added successfully'
  });
}