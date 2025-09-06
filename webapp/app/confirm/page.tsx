"use client";
import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import ConfirmCalendar from "@/components/confirm/ConfirmCalendar";
import { fetchEventFromAPI } from "@/routes/events_routes";
import { EventData } from "@/utils/event_service";
import {
  fetchUserDataFromId,
  fetchUserDataFromUsername,
} from "@/routes/user_routes";
import ConfirmDatePicker from "@/components/confirm/ConfirmDatePicker";
import { useTelegramViewport } from "@/hooks/useTelegramViewport";
import { Button, Card, CardBody, CardHeader, Spinner } from "@nextui-org/react";

export default function ConfirmPage() {
  // Telegram viewport setup
  useTelegramViewport();

  const [eventDetails, setEventDetails] = useState<EventData | null>(null);
  const [bestStart, setBestStart] = useState("");
  const [bestEnd, setBestEnd] = useState("");
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [participantCount, setParticipantCount] = useState(0);
  const [eventId, setEventId] = useState<string>("");
  const [userUuid, setUserUuid] = useState<string>("");
  const [teleUser, setTeleUser] = useState<string>("");
  const [teleId, setTeleId] = useState<string>("");
  const [isEventCreator, setIsEventCreator] = useState(false);
  const [tg, setTg] = useState<any>(null);
  const [shareToken, setShareToken] = useState<string>("");

  // Parse URL parameters and get user data from username or telegram id
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const event_id = urlParams.get("event_id");
    setEventId(event_id || "");

    const username = urlParams.get("username");
    setTeleUser(username || "");

    const maybeShareToken = urlParams.get("share_token");
    if (maybeShareToken) {
      setShareToken(maybeShareToken);
    }

    if (window.Telegram?.WebApp) {
      setTg(window.Telegram.WebApp);
    } else {
      console.error("Telegram Web App script not loaded");
    }

    if (window.Telegram.WebApp.initDataUnsafe.user) {
      const telegramId = window.Telegram.WebApp.initDataUnsafe.user.id;
      setTeleId(telegramId.toString());
      const telegramUser = window.Telegram.WebApp.initDataUnsafe.user.username;
      if (telegramUser) setTeleUser(telegramUser);
    }
  }, []);

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
          setError("");
          setEventDetails(eventData);
        } else {
          console.log("Error setting event");
          setError("Event not found");
        }

        // Fetch best time from backend
        try {
          const res = await fetch(`/api/event/${eventId}/best-time`);
          if (res.ok) {
            const data = await res.json();
            console.log(data);

            // Convert ISO datetime to datetime-local format
            const convertToLocalDateTime = (isoString: string) => {
              if (!isoString) return "";
              const date = new Date(isoString);
              // Convert to local time and format as YYYY-MM-DDTHH:mm for datetime-local input
              const year = date.getFullYear();
              const month = String(date.getMonth() + 1).padStart(2, "0");
              const day = String(date.getDate()).padStart(2, "0");
              const hours = String(date.getHours()).padStart(2, "0");
              const minutes = String(date.getMinutes()).padStart(2, "0");
              return `${year}-${month}-${day}T${hours}:${minutes}`;
            };

            setBestStart(convertToLocalDateTime(data.data[0].start_time) || "");
            setBestEnd(convertToLocalDateTime(data.data[0].end_time) || "");
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

  // get user uuid from tele id
  useEffect(() => {
    async function fetchUserUuidFromTeleIdAsync() {
      if (teleId) {
        const userData = await fetchUserDataFromId(teleId);
        if (userData) {
          setUserUuid(userData.uuid);
        }
      }
    }
    fetchUserUuidFromTeleIdAsync();
  }, [teleId]);

  // get user uuid from tele user if id not available
  useEffect(() => {
    async function fetchUserUuidFromTeleUserAsync() {
      if (teleUser) {
        const userData = await fetchUserDataFromUsername(teleUser);
        if (userData) {
          setUserUuid(userData.uuid);
          setTeleId(userData.tele_id);
        }
      }
    }
    fetchUserUuidFromTeleUserAsync();
  }, [teleId, teleUser]);

  // check if user uuid is the same as the event creator
  useEffect(() => {
    if (userUuid && eventDetails?.creator === userUuid) {
      setIsEventCreator(true);
    } else {
      setIsEventCreator(false);
    }
  }, [userUuid, eventDetails]);

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

  //handle date change
  const handleDateChange = (dates: {
    startDate: Date | null;
    endDate: Date | null;
  }) => {
    if (dates.startDate) {
      setBestStart(dates.startDate.toISOString());
    }
    if (dates.endDate) {
      setBestEnd(dates.endDate.toISOString());
    }
  };

  // Handle confirm
  async function handleConfirm() {
    if (!isEventCreator) {
      return;
    }

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

      if (shareToken) {
        const response = await fetch("/api/share", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            token: shareToken,
            event_id: eventId,
          }),
        });

        if (response.ok) {
          const result = await response.json();
          console.log("Event shared successfully:", result);
        } else {
          console.error("Failed to share event");
        }
      } else {
        console.error("No share token available");
      }
      // Close the Telegram WebApp if open
      if (tg) {
        tg.close();
      }
    } catch (e) {
      console.error("Error confirming event:", e);
    }
    setSubmitting(false);
  }

  if (loading) {
    return (
      <main className="minecraft-font bg-black min-h-screen flex items-center justify-center p-4">
        <Card className="bg-[#0a0a0a] border border-[#8c2e2e] shadow-lg">
          <CardBody className="flex items-center justify-center p-8">
            <Spinner size="lg" color="primary" />
            <p className="mt-4 text-white">Loading event details...</p>
          </CardBody>
        </Card>
      </main>
    );
  }

  if (error || !eventDetails) {
    return (
      <main className="minecraft-font bg-black min-h-screen flex items-center justify-center p-4">
        <Card className="bg-[#0a0a0a] border border-[#8c2e2e] shadow-lg max-w-md w-full">
          <CardHeader className="pb-2">
            <h1 className="text-2xl font-bold text-white">Event Not Found</h1>
          </CardHeader>
          <CardBody>
            <p className="text-[#e5e5e5] mb-4">
              {error || "The requested event could not be found."}
            </p>
            <Button
              color="primary"
              variant="solid"
              onPress={() => window.history.back()}
              className="w-full"
            >
              Go Back
            </Button>
          </CardBody>
        </Card>
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
    <main className="minecraft-font bg-black min-h-screen p-4">
      <div className="max-w-7xl mx-auto">
        <Card className="bg-[#0a0a0a] border border-[#8c2e2e] rounded-lg shadow-lg mb-6">
          <CardHeader className="pb-2">
            <div className="w-full">
              <h1 className="text-3xl font-bold mb-2 text-white">
                {eventDetails.event_name}
              </h1>
              <p className="text-[#e5e5e5] text-lg">
                {eventDetails.event_description}
              </p>
              <div className="mt-2 text-sm text-[#a0a0a0]">
                {eventStartDate.toLocaleDateString()} -{" "}
                {eventEndDate.toLocaleDateString()}
              </div>
            </div>
          </CardHeader>
        </Card>

        <Card className="bg-[#0a0a0a] border border-[#8c2e2e] rounded-lg shadow-lg mb-6">
          <CardHeader className="pb-2">
            <h2 className="text-xl font-semibold text-white">
              Participant Availability Heat Map
            </h2>
          </CardHeader>
          <CardBody>
            {participantCount > 0 && (
              <div className="flex flex-wrap items-center gap-4 mb-4 text-sm text-[#e5e5e5]">
                {legendItems.map((item, index) => (
                  <div key={index} className="flex items-center gap-2">
                    <div
                      className={`w-4 h-4 ${item.color} ${
                        item.color.includes("blue-50")
                          ? "border border-[#333333]"
                          : ""
                      } rounded`}
                    ></div>
                    <span>{item.label}</span>
                  </div>
                ))}
              </div>
            )}

            {participantCount === 0 && (
              <div className="mb-4 text-sm text-[#a0a0a0]">
                No participant availability data yet.
              </div>
            )}

            <div className="bg-[#0a0a0a] rounded-lg shadow-sm overflow-hidden">
              <div className="h-64 overflow-y-auto">
                <ConfirmCalendar
                  startDate={eventStartDate}
                  endDate={eventEndDate}
                  numDays={Math.min(totalDays, 7)}
                  eventId={eventId || ""}
                  onParticipantCountChange={handleParticipantCountChange}
                />
              </div>
            </div>
          </CardBody>
        </Card>

        <Card className="bg-[#0a0a0a] border border-[#8c2e2e] rounded-lg shadow-lg">
          <CardHeader className="pb-2">
            <h2 className="text-xl font-semibold text-white">
              Confirm Event Timing
            </h2>
          </CardHeader>
          <CardBody>
            <ConfirmDatePicker
              startDate={bestStart}
              endDate={bestEnd}
              onDateChange={handleDateChange}
            />

            <Button
              color="primary"
              variant="solid"
              size="lg"
              className="w-full mt-4 transition-all duration-150 hover:shadow-[4px_4px_0px_0px_rgba(0,0,0,0.8)]"
              onPress={handleConfirm}
              isDisabled={loading || submitting || !isEventCreator}
              isLoading={submitting}
            >
              {!isEventCreator
                ? "You are not the event creator"
                : submitting
                ? "Confirming..."
                : "Confirm Event"}
            </Button>
          </CardBody>
        </Card>
      </div>
    </main>
  );
}
