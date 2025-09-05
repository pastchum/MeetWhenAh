"use client";
import React, { useEffect, useState, useCallback } from "react";
import { ShareData } from "@/utils/share_service";
import EventCard from "@/components/share/EventCard";
import { useOverlay } from "@/hooks/useOverlay";
import { EventData } from "@/utils/event_service";

export default function SharePage() {
  const { showOverlay } = useOverlay();
  const [token, setToken] = useState<string | null>(null);
  const [tele_id, setTeleId] = useState<string | null>(null);
  const [isOwner, setIsOwner] = useState<boolean>(false);
  const [userEvents, setUserEvents] = useState<EventData[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchCtx = useCallback(async (): Promise<ShareData | null> => {
    if (!token) return null;

    const response = await fetch(`/api/${token}`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });
    if (response.ok) {
      const data = await response.json();
      return data;
    } else {
      return null;
    }
  }, [token]);

  const fetchUserEvents = useCallback(
    async (teleId: string): Promise<EventData[]> => {
      try {
        const response = await fetch(`/api/user/events/${teleId}`, {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
          },
        });

        if (response.ok) {
          const result = await response.json();
          return result.data || [];
        } else {
          console.error("Failed to fetch user events");
          return [];
        }
      } catch (error) {
        console.error("Error fetching user events:", error);
        return [];
      }
    },
    []
  );

  const handleEventShare = async (eventId: string) => {
    if (!token) {
      console.error("No token available for sharing");
      return;
    }

    try {
      const response = await fetch("/api/share", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          token: token,
          event_id: eventId,
        }),
      });

      if (response.ok) {
        const result = await response.json();
        console.log("Event shared successfully:", result);
        
        // Show success overlay
        showOverlay((
          <div className="fixed inset-0 bg-black bg-opacity-70 flex items-center justify-center z-[9999] transition-all duration-500">
            <div className="bg-white rounded-lg p-6 max-w-sm mx-4 text-center minecraft-font shadow-[4px_4px_0px_0px_rgba(0,0,0,0.8)] transform -translate-y-1 transition-all duration-500">
              <div className="mb-4">
                <div className="text-2xl mb-2">🎉</div>
              </div>
              <h3 className="text-lg font-bold text-gray-800 mb-2">Event Shared!</h3>
              <p className="text-gray-600 text-sm mb-4">
                Your event has been shared to your chat!
              </p>
            </div>
          </div>
        ), {
          fadeInDuration: 200,
          displayDuration: 1300,
          fadeOutDuration: 200
        });
      } else {
        console.error("Failed to share event");
        throw new Error("Failed to share event");
      }
    } catch (error) {
      console.error("Error sharing event:", error);
      
      // Show error overlay
      showOverlay((
        <div className="fixed inset-0 bg-black bg-opacity-70 flex items-center justify-center z-[9999] transition-all duration-500">
          <div className="bg-red-100 border border-red-400 rounded-lg p-6 max-w-sm mx-4 text-center minecraft-font shadow-[4px_4px_0px_0px_rgba(0,0,0,0.8)] transform -translate-y-1 transition-all duration-500">
            <div className="text-2xl mb-2">⚠️</div>
            <h3 className="text-lg font-bold text-red-800 mb-2">Share Failed</h3>
            <p className="text-red-600 text-sm mb-4">
              Failed to share event. Please try again.
            </p>
          </div>
        </div>
      ), {
        fadeInDuration: 200,
        displayDuration: 700,
        fadeOutDuration: 200
      });
    }
  };

  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get("token");
    setToken(token);

    if (window.Telegram?.WebApp) {
      const webApp = window.Telegram.WebApp;
      const user = webApp.initDataUnsafe.user;
      setTeleId(user?.id.toString() ?? null);
    } else {
      // only for web testing
      const tele_id = urlParams.get("tele_id");
      setTeleId(tele_id ?? null);
    }
  }, []);

  useEffect(() => {
    const fetchData = async () => {
      if (!token || !tele_id) {
        return;
      }

      try {
        setLoading(true);
        setError(null);

        // Fetch context data
        const ctx = await fetchCtx();
        if (ctx) {
          setIsOwner(ctx.tele_id === tele_id);
        } else {
          console.log("Failed to fetch ctx");
        }

        // Fetch user events
        const events = await fetchUserEvents(tele_id);
        setUserEvents(events);
      } catch (err) {
        setError("Failed to load data");
        console.error("Error fetching data:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [token, tele_id, fetchCtx, fetchUserEvents]);

  if (loading) {
    return (
      <div className="minecraft-font bg-black min-h-screen flex flex-col items-center justify-center">
        <div className="text-white text-lg">Loading...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="minecraft-font bg-black min-h-screen flex flex-col items-center justify-center">
        <div className="text-red-500 text-lg">{error}</div>
      </div>
    );
  }

  return (
    <div className="minecraft-font bg-black min-h-screen flex flex-col items-center justify-start p-4">
      <div className="w-full max-w-md mb-6 text-center">
        <h1 
          className="font-semibold text-3xl cursor-pointer hover:opacity-80 transition-opacity"
          onClick={() => window.location.href = `/dashboard${token ? `?token=${token}` : ''}`}
        >
          <span className="text-white">MeetWhen</span><span className="text-[#c44545]">?</span>
        </h1>
      </div>
      
      <div className="w-full max-w-2xl">
        <h2 className="text-2xl font-bold mb-6 text-center text-white">
          Your Events
        </h2>

        <div className="space-y-4">
          {userEvents.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-gray-400 text-lg">No events found</p>
              <p className="text-gray-500 text-sm mt-2">
                You haven&apos;t joined any events yet.
              </p>
            </div>
          ) : (
            userEvents.map((event) => (
              <EventCard
                key={event.event_id}
                event={event}
                token={token}
                onShare={handleEventShare}
              />
            ))
          )}
        </div>
      </div>
    </div>
  );
}
