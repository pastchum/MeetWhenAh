import { supabase, TableRow } from '@/lib/db' ;

export interface UserData {
    uuid: string;
    tele_id: string;
    tele_user: string;
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

    return {
        uuid: data[0].uuid,
        tele_id: data[0].tele_id,
        tele_user: data[0].tele_user
    };
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

    return {
        uuid: data[0].uuid,
        tele_id: data[0].tele_id,
        tele_user: data[0].tele_user
    };
}