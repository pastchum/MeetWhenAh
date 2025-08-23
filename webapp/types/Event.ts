export interface Event{
    event_id: string;
    event_name: string;
    event_description: string;
    event_type: string;
    start_date: string;
    end_date: string;
    start_hour: string;
    end_hour: string;
    creator: string;
    min_participants: number;
    min_duration: number;
    max_duration: number;
    timezone: string;
    is_reminders_enabled: boolean;
    cancelled: boolean;
    created_at: string;
}

export interface ConfirmedEvent extends Event {
    confirmed_at: string;
    confirmed_start_time: string;
    confirmed_end_time: string;
}