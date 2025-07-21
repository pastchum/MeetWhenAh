"use client";
import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import ConfirmCalendar from "@/components/confirm/ConfirmCalendar";
import { fetchEventFromAPI } from "@/routes/events_routes";
import { EventData } from "@/utils/event_service";

export default function ConfirmPage() {
  const searchParams = useSearchParams();
  const eventId = searchParams.get("event_id");

  const [eventDetails, setEventDetails] = useState<EventData | null>(null);
  const [bestStart, setBestStart] = useState("");
  const [bestEnd, setBestEnd] = useState("");
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [participantCount, setParticipantCount] = useState(0);

  // Fetch event details and best time
  useEffect(() => {
    async function fetchEventDetails() {
      if (!eventId) {
        setError("No event ID provided");
        setLoading(false);
        return;
      }

      setLoading(true);
      try {
        // Fetch event details
        const eventData = await fetchEventFromAPI(eventId);
        if (eventData) {
          setEventDetails(eventData);
        } else {
          setError("Event not found");
        }

        // Fetch best time from backend
        try {
          const res = await fetch(`/api/event/${eventId}/best-time`);
          if (res.ok) {
            const data = await res.json();
            setBestStart(data.best_start_time || "");
            setBestEnd(data.best_end_time || "");
          }
        } catch (e) {
          console.log("No best time available yet");
        }
      } catch (e) {
        console.error("Error fetching event details:", e);
        setError("Failed to load event details");
      }
      setLoading(false);
    }
    fetchEventDetails();
  }, [eventId]);

  // Handle participant count change from calendar
  const handleParticipantCountChange = (count: number) => {
    setParticipantCount(count);
  };

  // Generate dynamic legend items based on participant count
  const generateLegendItems = () => {
    if (participantCount === 0) return [];

    const items = [];

    // All participants available (100%)
    items.push({
      color: "bg-blue-600",
      label: `All ${participantCount} participants available`,
    });

    // High availability (75%+)
    if (participantCount > 1) {
      const highMin = Math.ceil(participantCount * 0.75);
      const highMax = participantCount - 1;
      if (highMin <= highMax) {
        items.push({
          color: "bg-blue-400",
          label: `${highMin}${
            highMin !== highMax ? `-${highMax}` : ""
          } participants available`,
        });
      }
    }

    // Medium availability (50-74%)
    if (participantCount > 2) {
      const medMin = Math.ceil(participantCount * 0.5);
      const medMax = Math.floor(participantCount * 0.74);
      if (medMin <= medMax) {
        items.push({
          color: "bg-blue-200",
          label: `${medMin}${
            medMin !== medMax ? `-${medMax}` : ""
          } participants available`,
        });
      }
    }

    // Low availability (25-49%)
    if (participantCount > 4) {
      const lowMin = Math.ceil(participantCount * 0.25);
      const lowMax = Math.floor(participantCount * 0.49);
      if (lowMin <= lowMax) {
        items.push({
          color: "bg-blue-100",
          label: `${lowMin}${
            lowMin !== lowMax ? `-${lowMax}` : ""
          } participants available`,
        });
      }
    }

    // Very low availability (1-24%)
    if (participantCount > 4) {
      const veryLowMax = Math.floor(participantCount * 0.24);
      if (veryLowMax >= 1) {
        items.push({
          color: "bg-blue-50",
          label: `1${veryLowMax > 1 ? `-${veryLowMax}` : ""} participant${
            veryLowMax > 1 ? "s" : ""
          } available`,
        });
      }
    } else if (participantCount > 1) {
      // For smaller groups, just show "1 participant available"
      items.push({
        color: "bg-blue-50",
        label: "1 participant available",
      });
    }

    return items;
  };

  // Handle confirm
  async function handleConfirm() {
    setSubmitting(true);
    try {
      await fetch("/api/event/confirm", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          event_id: eventId,
          best_start_time: bestStart,
          best_end_time: bestEnd,
        }),
      });

      // Optionally, send data to Telegram WebApp
      if (window.Telegram?.WebApp) {
        window.Telegram.WebApp.sendData(
          JSON.stringify({
            web_app_number: 1,
            event_id: eventId,
            best_start_time: bestStart,
            best_end_time: bestEnd,
            participants: [],
          })
        );
        window.Telegram.WebApp.close();
      }
    } catch (e) {
      console.error("Error confirming event:", e);
    }
    setSubmitting(false);
  }

  if (loading) {
    return (
      <main className="max-w-7xl mx-auto p-4">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
        </div>
      </main>
    );
  }

  if (error || !eventDetails) {
    return (
      <main className="max-w-7xl mx-auto p-4">
        <div className="text-center">
          <h1 className="text-2xl font-bold mb-4 text-gray-50">
            Event Not Found
          </h1>
          <p className="text-gray-600">
            {error || "The requested event could not be found."}
          </p>
        </div>
      </main>
    );
  }

  const eventStartDate = new Date(eventDetails.start_date);
  const eventEndDate = new Date(eventDetails.end_date);

  // Calculate number of days for the event
  const totalDays = Math.ceil(
    (eventEndDate.getTime() - eventStartDate.getTime()) / (1000 * 3600 * 24) + 1
  );

  const legendItems = generateLegendItems();

  return (
    <main className="max-w-7xl mx-auto p-4">
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2 text-gray-50">
          {eventDetails.event_name}
        </h1>
        <p className="text-gray-600 text-lg">
          {eventDetails.event_description}
        </p>
        <div className="mt-2 text-sm text-gray-500">
          {eventStartDate.toLocaleDateString()} -{" "}
          {eventEndDate.toLocaleDateString()}
        </div>
      </div>

      <div className="mb-6">
        <h2 className="text-xl font-semibold mb-3 text-gray-50">
          Participant Availability Heat Map
        </h2>

        {participantCount > 0 && (
          <div className="flex flex-wrap items-center gap-4 mb-4 text-sm text-gray-600">
            {legendItems.map((item, index) => (
              <div key={index} className="flex items-center gap-2">
                <div
                  className={`w-4 h-4 ${item.color} ${
                    item.color.includes("blue-50")
                      ? "border border-gray-200"
                      : ""
                  } rounded`}
                ></div>
                <span>{item.label}</span>
              </div>
            ))}
          </div>
        )}

        {participantCount === 0 && (
          <div className="mb-4 text-sm text-gray-500">
            No participant availability data yet.
          </div>
        )}

        <div className="border border-gray-200 rounded-lg shadow-sm">
          <ConfirmCalendar
            startDate={eventStartDate}
            endDate={eventEndDate}
            numDays={Math.min(totalDays, 7)}
            eventId={eventId || ""}
            onParticipantCountChange={handleParticipantCountChange}
          />
        </div>
      </div>

      <hr className="my-6" />

      <div className="mb-6">
        <h2 className="text-xl font-semibold mb-4 text-gray-50">
          Confirm Event Timing
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-gray-100 mb-2">
              Start time:
            </label>
            <input
              type="datetime-local"
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              value={bestStart}
              onChange={(e) => setBestStart(e.target.value)}
              disabled={loading}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-100 mb-2">
              End time:
            </label>
            <input
              type="datetime-local"
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              value={bestEnd}
              onChange={(e) => setBestEnd(e.target.value)}
              disabled={loading}
            />
          </div>
        </div>

        <button
          className="w-full bg-blue-600 hover:bg-blue-700 text-white py-3 rounded-md font-semibold transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
          onClick={handleConfirm}
          disabled={loading || submitting}
        >
          {submitting ? "Confirming..." : "Confirm Event"}
        </button>
      </div>
    </main>
  );
}
