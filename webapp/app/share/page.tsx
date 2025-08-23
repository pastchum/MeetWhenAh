"use client";
import React, { useEffect, useState, useCallback } from "react";
import { ShareData } from "@/utils/share_service";

interface UserEvent {
  id: string;
  name: string;
}

export default function SharePage() {
  const [token, setToken] = useState<string | null>(null);
  const [tele_id, setTeleId] = useState<string | null>(null);
  const [isOwner, setIsOwner] = useState<boolean>(false);
  const [userEvents, setUserEvents] = useState<UserEvent[]>([]);
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
    async (teleId: string): Promise<UserEvent[]> => {
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

  const handleEventSelection = async (eventId: string) => {
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
      } else {
        console.error("Failed to share event");
      }
    } catch (error) {
      console.error("Error sharing event:", error);
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
    <div className="minecraft-font bg-black min-h-screen flex flex-col items-center justify-start p-6">
      <div className="w-full max-w-2xl">
        <h1 className="text-2xl font-bold mb-6 text-center text-white">
          Your Events
        </h1>

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
              <div
                key={event.id}
                className="bg-[#f8f9fa] rounded-lg p-4 shadow-sm hover:shadow-md transition-all duration-150 cursor-pointer"
                onClick={() => handleEventSelection(event.id)}
              >
                <h3 className="text-lg font-semibold text-gray-800">
                  {event.name}
                </h3>
                <p className="text-sm text-gray-600 mt-1">
                  Event ID: {event.id}
                </p>
                <div className="mt-3 flex space-x-2">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      window.location.href = `/confirm?event_id=${event.id}&share_token=${token}`;
                    }}
                    className="bg-green-500 hover:bg-green-600 text-white px-3 py-1 rounded text-sm transition-all duration-150 minecraft-font shadow-[2px_2px_0px_0px_rgba(0,0,0,0.6)] hover:shadow-[3px_3px_0px_0px_rgba(0,0,0,0.7)]"
                  >
                    Confirm Event
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
