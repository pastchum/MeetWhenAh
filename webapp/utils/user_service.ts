import { supabase } from '@/lib/db';

export interface UserData {
  uuid: string;
  tele_id: string;
  tele_user: string;
  initialised: boolean;
  callout_cleared: boolean;
  created_at: string;
  updated_at: string;
  sleep_start?: string;
  sleep_end?: string;
}

export interface NewUserData {
  tele_id: string;
  tele_user: string;
}

export class UserService {
  /**
   * Get a user by their Telegram ID
   */
  async getUser(teleId: string): Promise<UserData | null> {
    try {
      const { data, error } = await supabase
        .from('users')
        .select('*')
        .eq('tele_id', teleId)
        .single();

      if (error) {
        console.error('Error getting user:', error);
        return null;
      }

      return data;
    } catch (error) {
      console.error('Error getting user:', error);
      return null;
    }
  }

  /**
   * Set a user by their Telegram ID
   */
  async setUser(user: NewUserData): Promise<boolean> {
    try {
      const userUuid = crypto.randomUUID();
      const now = new Date().toISOString();
      
      const userData = {
        uuid: userUuid,
        tele_id: user.tele_id,
        tele_user: user.tele_user,
        initialised: true,
        callout_cleared: false,
        created_at: now,
        updated_at: now
      };

      const { error } = await supabase
        .from('users')
        .insert(userData);

      if (error) {
        console.error('Error setting user:', error);
        return false;
      }

      return true;
    } catch (error) {
      console.error('Error setting user:', error);
      return false;
    }
  }

  /**
   * Update a user's initialised status
   */
  async updateUserInitialised(teleId: string): Promise<boolean> {
    try {
      const now = new Date().toISOString();
      
      const { error } = await supabase
        .from('users')
        .update({
          initialised: true,
          callout_cleared: true,
          updated_at: now
        })
        .eq('tele_id', teleId);

      if (error) {
        console.error('Error updating user initialised status:', error);
        return false;
      }

      return true;
    } catch (error) {
      console.error('Error updating user initialised status:', error);
      return false;
    }
  }

  /**
   * Update or create a user's username
   */
  async updateUsername(teleId: string, tele_user: string): Promise<boolean> {
    try {
      const user = await this.getUser(teleId);
      
      if (user) {
        // Update existing user
        const { error } = await supabase
          .from('users')
          .update({
            tele_user: tele_user,
            updated_at: new Date().toISOString()
          })
          .eq('tele_id', teleId);

        if (error) {
          console.error('Error updating username:', error);
          return false;
        }
      } else {
        // Create new user
        const userData = {
          tele_id: teleId,
          tele_user: tele_user,
        };
        return await this.setUser(userData);
      }

      return true;
    } catch (error) {
      console.error('Error updating username:', error);
      return false;
    }
  }

  /**
   * Set a user's sleep preferences
   */
  async setUserSleepPreferences(teleId: string, sleepStart: string, sleepEnd: string): Promise<boolean> {
    try {
      const user = await this.getUser(teleId);
      const now = new Date().toISOString();
      
      if (user) {
        // Update existing user
        const { error } = await supabase
          .from('users')
          .update({
            sleep_start: sleepStart,
            sleep_end: sleepEnd,
            updated_at: now
          })
          .eq('tele_id', teleId);

        if (error) {
          console.error('Error updating sleep preferences:', error);
          return false;
        }
      } else {
        // Create new user with sleep preferences
        const userUuid = crypto.randomUUID();
        const userData = {
          uuid: userUuid,
          tele_id: teleId,
          tele_user: '',
          sleep_start: sleepStart,
          sleep_end: sleepEnd,
          initialised: false,
          callout_cleared: false,
          created_at: now,
          updated_at: now
        };

        const { error } = await supabase
          .from('users')
          .insert(userData);

        if (error) {
          console.error('Error creating user with sleep preferences:', error);
          return false;
        }
      }

      return true;
    } catch (error) {
      console.error('Error setting sleep preferences:', error);
      return false;
    }
  }

  /**
   * Get a user by their username
   */
  async getUserByUsername(username: string): Promise<UserData | null> {
    try {
      const { data, error } = await supabase
        .from('users')
        .select('*')
        .eq('tele_user', username)
        .single();

      if (error) {
        console.error('Error getting user by username:', error);
        return null;
      }

      return data;
    } catch (error) {
      console.error('Error getting user by username:', error);
      return null;
    }
  }
} 