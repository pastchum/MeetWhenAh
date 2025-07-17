import { supabase, TableRow } from '@/app/lib/db';

/**
 * Get a single entry from a table by a key field
 */
export async function getEntry(table: string, keyField: string, keyValue: string): Promise<TableRow | null> {
    try {
      const { data, error } = await supabase
        .from(table)
        .select('*')
        .eq(keyField, keyValue)
        .limit(1)
        .maybeSingle();
  
      if (error) throw error;
      return data || null;
    } catch (err) {
      console.error(`Error getting entry from ${table}:`, err);
      return null;
    }
  }
  
  /**
   * Get multiple entries from a table by a key field
   */
  export async function getEntries(table: string, keyField: string, keyValue: string): Promise<TableRow[] | null> {
    try {
      const { data, error } = await supabase
        .from(table)
        .select('*')
        .eq(keyField, keyValue);
  
      if (error) throw error;
      return data;
    } catch (err) {
      console.error(`Error getting entries from ${table}:`, err);
      return null;
    }
  }
  
  /**
   * Insert a single entry into a table
   */
  export async function setEntry(table: string, data: TableRow): Promise<boolean> {
    try {
      const { data: result, error } = await supabase
        .from(table)
        .insert(data)
        .select();
  
      if (error) throw error;
      return !!result;
    } catch (err) {
      console.error(`Error setting entry in ${table}:`, err);
      return false;
    }
  }
  
  /**
   * Insert multiple entries into a table
   */
  export async function setEntries(table: string, data: TableRow[]): Promise<boolean> {
    try {
      const { data: result, error } = await supabase
        .from(table)
        .insert(data)
        .select();
  
      if (error) throw error;
      return !!result;
    } catch (err) {
      console.error(`Error setting entries in ${table}:`, err);
      return false;
    }
  }
  
  /**
   * Update an entry in a table by `event_id`
   */
  export async function updateEntry(table: string, id: string, data: TableRow): Promise<boolean> {
    try {
      const { data: result, error } = await supabase
        .from(table)
        .update(data)
        .eq('event_id', id)
        .select();
  
      if (error) throw error;
      return !!result;
    } catch (err) {
      console.error(`Error updating entry in ${table}:`, err);
      return false;
    }
  }
  
  /**
   * Delete a single entry based on two fields
   */
  export async function deleteEntry(
    table: string,
    idField: string,
    id: string,
    keyField: string,
    keyValue: string
  ): Promise<boolean> {
    try {
      const { error } = await supabase
        .from(table)
        .delete()
        .eq(idField, id)
        .eq(keyField, keyValue);
  
      if (error) throw error;
      return true;
    } catch (err) {
      console.error(`Error deleting entry from ${table}:`, err);
      return false;
    }
  }
  
  /**
   * Delete multiple entries where key_field is in a list
   */
  export async function deleteEntries(
    table: string,
    idField: string,
    id: string,
    keyField: string,
    keyValues: string[]
  ): Promise<boolean> {
    try {
      const { error } = await supabase
        .from(table)
        .delete()
        .eq(idField, id)
        .in(keyField, keyValues);
  
      if (error) throw error;
      return true;
    } catch (err) {
      console.error(`Error deleting entries from ${table}:`, err);
      return false;
    }
  }