"use client";
import React, { useEffect, useState, useCallback, useMemo } from "react";
import { ShareData } from "@/utils/share_service";
import useUserEvents from "@/hooks/useUserEvents";
import useUser from "@/hooks/useUser";

export default function SharePage() {
  const [token, setToken] = useState<string | null>(null);
  const [tele_id, setTeleId] = useState<string | null>(null);
  const [isOwner, setIsOwner] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const {
    user,
    loading: userLoading,
    error: userError,
  } = useUser(tele_id ?? undefined);
  const {
    events,
    confirmedEvents,
    unconfirmedEvents,
    loading: userEventsLoading,
    error: userEventsError,
  } = useUserEvents(tele_id ?? undefined);

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
      console.log(data);
      return data;
    } else {
      return null;
    }
  }, [token]);

  const handleEventSelection = async (eventId: string) => {
    if (!token) {
      console.error("No token available for sharing");
      return;
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
      } catch (err) {
        setError("Failed to load data");
        console.error("Error fetching data:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [token, tele_id, fetchCtx]);

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
          {events.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-gray-400 text-lg">No events found</p>
              <p className="text-gray-500 text-sm mt-2">
                You haven&apos;t joined any events yet.
              </p>
            </div>
          ) : (
            <>
              {confirmedEvents.length > 0 && (
                <div className="space-y-4">
                  <h2 className="text-lg font-semibold text-gray-800">
                    Confirmed Events
                  </h2>
                </div>
              )}
              {confirmedEvents.map((event) => (
                <div
                  key={event.event_id}
                  className="bg-[#f8f9fa] rounded-lg p-4 shadow-sm hover:shadow-md transition-all duration-150 cursor-pointer"
                  onClick={() => handleEventSelection(event.event_id)}
                >
                  <h3 className="text-lg font-semibold text-gray-800">
                    {event.event_name}
                  </h3>
                  <p className="text-sm text-gray-600 mt-1">
                    Event ID: {event.event_id}
                  </p>
                </div>
              ))}
              {unconfirmedEvents.length > 0 && (
                <div className="space-y-4">
                  <h2 className="text-lg font-semibold text-gray-800">
                    Unconfirmed Events
                  </h2>
                  {unconfirmedEvents.map((event) => (
                    <div
                      key={event.event_id}
                      className="bg-[#f8f9fa] rounded-lg p-4 shadow-sm hover:shadow-md transition-all duration-150 cursor-pointer"
                      onClick={() => handleEventSelection(event.event_id)}
                    >
                      <h3 className="text-lg font-semibold text-gray-800">
                        {event.event_name}
                      </h3>
                      <p className="text-sm text-gray-600 mt-1">
                        Event ID: {event.event_id}
                      </p>
                      <div className="mt-3 flex space-x-2">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            window.location.href = `/confirm?event_id=${event.event_id}&share_token=${token}`;
                          }}
                          className="bg-green-500 hover:bg-green-600 text-white px-3 py-1 rounded text-sm transition-all duration-150 minecraft-font shadow-[2px_2px_0px_0px_rgba(0,0,0,0.6)] hover:shadow-[3px_3px_0px_0px_rgba(0,0,0,0.7)]"
                        >
                          Confirm Event
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
