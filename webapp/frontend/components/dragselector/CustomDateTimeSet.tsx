import { DateTime } from '@/components/dragselector/DragSelector'

function areDateTimesEqual(dt1:DateTime, dt2:DateTime): boolean {
    return dt1.date === dt2.date && dt1.time === dt2.time;
}

export default class CustomDateTimeSet{
    private set: Set<DateTime>;

    constructor(existingSet?: CustomDateTimeSet) {
      if (existingSet) {
        this.set = new Set<DateTime>(existingSet.values());
      } else {
        this.set = new Set<DateTime>();
      }
    }

    add(dateTime: DateTime): void {
        for (let item of this.set) {
          if (areDateTimesEqual(item, dateTime)) {
            return;
          }
        }
        this.set.add(dateTime);
      }
    
      delete(dateTime: DateTime): void {
        for (let item of this.set) {
          if (areDateTimesEqual(item, dateTime)) {
            this.set.delete(item);
            return;
          }
        }
      }
      has(dateTime: DateTime): boolean {
        for (let item of this.set) {
          
          if (areDateTimesEqual(item, dateTime)) {
            return true;
          }
        }
        return false;
      }
    
      size(): number {
        return this.set.size;
      }
    
      // Additional method to get all DateTime objects as an array
      values(): DateTime[] {
        return Array.from(this.set);
      }
      
      toJSON(): object {
        return {
          dateTimes: this.values()
        };
      }
}