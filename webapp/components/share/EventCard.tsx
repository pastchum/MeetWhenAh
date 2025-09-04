import React, { useState } from 'react';
import { EventData } from '@/utils/event_service';
import { formatDateTime, formatDateRange } from '@/utils/datetime-utils';

interface EventCardProps {
  event: EventData;
  token: string | null;
  onShare: (eventId: string) => Promise<void>;
}

export default function EventCard({ event, token, onShare }: EventCardProps) {
  const [isSharing, setIsSharing] = useState(false);

  const handleShare = async () => {
    if (isSharing) return; // Prevent multiple clicks
    
    setIsSharing(true);
    
    try {
      await onShare(event.event_id);
    } catch (error) {
      console.error('Error sharing event:', error);
    } finally {
      setIsSharing(false);
    }
  };

  const handleConfirm = (e: React.MouseEvent) => {
    e.stopPropagation();
    window.location.href = `/confirm?event_id=${event.event_id}&share_token=${token}`;
  };

  return (
    <div className="bg-[#f8f9fa] rounded-lg p-4 shadow-sm hover:shadow-md transition-all duration-150 relative">
      <h3 className="text-lg font-semibold text-gray-800">
        {event.event_name}
      </h3>    
      
      {/* Event timing information */}
      <div className="mt-2 space-y-1">
        <p className="text-sm text-gray-600">
          <span className="font-medium">From:</span> {formatDateTime(event.start_date, event.start_hour, event.timezone, { mobile: true, format: 'short' })}
        </p>
        <p className="text-sm text-gray-600">
          <span className="font-medium">To:</span> {formatDateTime(event.end_date, event.end_hour, event.timezone, { mobile: true, format: 'short' })}
        </p>
        {/* <p className="text-xs text-gray-500">
          Duration: {event.min_duration_blocks} - {event.max_duration_blocks} blocks
        </p> */}
        {/* <p className="text-xs text-gray-500">
          Type: {event.event_type} • Min Participants: {event.min_participants}
        </p> */}
      </div>
      
      {/* Share button - left side */}
      <div className="mt-3">
        <button
          onClick={handleShare}
          onMouseUp={(e) => {
            // Reset button state immediately after mouse up
            e.currentTarget.blur();
          }}
          disabled={isSharing}
          className={`px-3 py-1 rounded text-sm transition-all duration-150 minecraft-font w-20 ${
            isSharing 
              ? 'bg-gray-400 text-gray-600 cursor-not-allowed shadow-[1px_1px_0px_0px_rgba(0,0,0,0.4)]' 
              : 'bg-blue-500 hover:bg-blue-600 text-white shadow-[2px_2px_0px_0px_rgba(0,0,0,0.6)] hover:shadow-[3px_3px_0px_0px_rgba(0,0,0,0.7)] active:shadow-[1px_1px_0px_0px_rgba(0,0,0,0.5)]'
          }`}
        >
          {isSharing ? 'Sharing...' : 'Share'}
        </button>
      </div>

      {/* Confirm button - bottom right, fixed position */}
      <button
        onClick={handleConfirm}
        onMouseUp={(e) => {
          // Reset button state immediately after mouse up
          e.currentTarget.blur();
        }}
        className="absolute bottom-3 right-3 bg-green-500 hover:bg-green-600 text-white px-3 py-1 rounded text-sm transition-all duration-150 minecraft-font shadow-[2px_2px_0px_0px_rgba(0,0,0,0.6)] hover:shadow-[3px_3px_0px_rgba(0,0,0,0.7)] active:shadow-[1px_1px_0px_rgba(0,0,0,0.5)]"
      >
        Confirm Event
      </button>
    </div>
  );
}
