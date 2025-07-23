import { NextRequest, NextResponse } from "next/server";
import { EventService } from "@/utils/event_service";

const eventService = new EventService();

export async function POST(request: NextRequest) {
    const body = await request.json();
    const response = await fetch(process.env.API_URL + '/api/event/confirm', {
        method: 'POST',
        body: JSON.stringify(body),
    });
    const result = await response.json();
    return NextResponse.json({ success: result.success });
}