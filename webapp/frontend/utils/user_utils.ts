import { supabase, TableRow } from '@/lib/db' ;

export interface UserData {
    uuid: string;
    tele_id: string;
    tele_user: string;
    created_at: string;
    updated_at: string;
    initialised: boolean;
    callout_cleared: boolean;
    sleep_start_time: string;
    sleep_end_time: string;
    tmp_sleep_start: string;
}

export async function getUserDataFromId(tele_id: string) {
    const { data, error } = await supabase
        .from('users')
        .select('*')
        .eq('tele_id', tele_id);

    if (error) {
        console.error('Error fetching user data:', error);
        return null;
    }

    return data[0];
}

export async function getUserDataFromUsername(username: string) {
    const { data, error } = await supabase
        .from('users')
        .select('*')
        .eq('tele_user', username);
        
    if (error) {
        console.error('Error fetching user data:', error);
        return null;
    }

    return data[0];
}

export async function addUser(user: UserData) {
    const { error } = await supabase
        .from('users')
        .insert(user);

    if (error) {
        console.error('Error adding user:', error);
        return null;
    }

    return user;
}