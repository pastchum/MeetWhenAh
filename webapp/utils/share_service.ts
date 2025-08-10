import { supabase } from '@/lib/db';

export interface ShareData {
  token: string;
  tele_id: string;
  chat_id: string;
  thread_id: string;
  message_id: string;
}

export class ShareService {
    /**
     * Check if the context for a given token is valid and belongs to the given Telegram ID
     * @param token - The token to check the context for
     * @param tele_id - The Telegram ID to check the context for
     * @returns True if the context is valid and belongs to the given Telegram ID, false otherwise
     */
    async check_ctx(token: string, tele_id: string) : Promise<boolean> {
        const ctx = await this.get_ctx(token);
        if (!ctx) {
            return false;
        }

        if (ctx.tele_id !== tele_id) {
            return false;
        }

        return true;
    }

    /**
     * Get the context for a given token
     * @param token - The token to get the context for
     * @returns The context for the given token, or null if the token is invalid or has expired
     */
  async get_ctx(token: string) : Promise<ShareData | null> {
    const { data, error } = await supabase.from('webapp_share_tokens').select('*').eq('token', token).single();
    if (error) {
      return null;
    }
    
    // Check if the token has expired or has been used
    if (new Date(data.expires_at) < new Date() || data.used_at) {
      return null;
    }

    return data;
  }

/**
 * Activate the context for a given token
 * @param token - The token to activate the context for
 * @returns True if the token was activated, false otherwise
 */
  async activate_ctx(token: string) : Promise<boolean> {
    const { error } = await supabase.rpc('get_and_use_share_token', { p_token: token });
    if (error) {
      return false;
    }
    return true;
  }

  /**
   * Share an event to a group chat. 
   * @param token - The token to share the event for
   * @param event_id - The event to share
   * @returns True if the event was shared, false otherwise
   */
  async share_event(token: string, event_id: string) : Promise<boolean> {
    // send the data back to the bot to edit the message
    const ctx = await this.get_ctx(token);
    if (!ctx) {
      return false;
    }

    const response = await fetch(process.env.API_URL + '/api/share', {
      method: 'POST',
      body: JSON.stringify({ token, event_id }),
    });

    if (!response.ok) {
      return false;
    }

    return true;
  }
}