import { NewUserData, UserData } from "@/utils/user_service";

export async function fetchUserDataFromId(tele_id: string) : Promise<UserData | null> {
    try {
        const response = await fetch(`/api/user/get-from-id/${tele_id}`);
        if (!response.ok) {
            throw new Error('Failed to fetch user data');
        }
        const result = await response.json();
        return result.data || null;
    } catch (error) {
        console.error('Error fetching user data:', error);
        return null;
    }
}

export async function fetchUserDataFromUsername(username: string) : Promise<UserData | null> {
    try {
        const response = await fetch(`/api/user/get-from-username/${username}`);
        if (!response.ok) {
            throw new Error('Failed to fetch user data');
        }
        const result = await response.json();
        return result.data || null;
    } catch (error) {
        console.error('Error fetching user data:', error);
        return null;
    }
}

export async function addUserToDatabase(user: NewUserData) {
    try {
        const response = await fetch(`/api/user/add`, {
            method: 'POST',
            body: JSON.stringify(user),
        });
        if (!response.ok) {
            throw new Error('Failed to add user');
        }
        const result = await response.json();
        return result.data || null;
    } catch (error) {
        console.error('Error adding user:', error);
        return null;
    } 
}

export async function updateUsername(teleId: string, tele_user: string) {
    try {
        const response = await fetch(`/api/user/update-username`, {
            method: 'POST',
            body: JSON.stringify({ tele_id: teleId, tele_user: tele_user }),
        });
        if (!response.ok) {
            throw new Error('Failed to update username');
        }
        const result = await response.json();
        return result.data || null;
    } catch (error) {
        console.error('Error updating username:', error);
        return null;
    }
}