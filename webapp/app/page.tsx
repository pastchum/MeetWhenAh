"use client";
import { Spinner } from "@nextui-org/react";
import Image from "next/image";
import { useEffect, useState } from "react";
import useUser from "@/hooks/useUser";

export default function Home() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [teleId, setTeleId] = useState<string | undefined>();
  const { user, loading: userLoading, error: userError } = useUser(teleId);

  useEffect(() => {
    if (user) {
      setLoading(false);
    }
  }, [user]);

  useEffect(() => {
    setLoading(true);
    const tg = window.Telegram.WebApp;
    if (tg.initDataUnsafe.user?.id) {
      setTeleId(tg.initDataUnsafe.user?.id.toString());
      console.log("teleId: ", teleId);
    }

    const startParam = tg.initDataUnsafe.start_param;
    if (startParam) {
      const params = startParam.split("=");
      const eventId = params[1];
      if (params[0] === "share") {
        window.location.href = `/share?token=${eventId}`;
      }
      if (params[0] === "dragselector" && eventId) {
        window.location.href = `/dragselector?event_id=${eventId}`;
      }
      if (params[0] === "confirm") {
        window.location.href = `/confirm?event_id=${eventId}`;
      }
    }
    setTeleId(window.Telegram.WebApp.initDataUnsafe.user?.id.toString());
    setLoading(false);
    setError(null);
  }, []);

  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24">
      {loading ? (
        <div className="flex flex-col items-center justify-center h-screen">
          <Spinner color="primary" size="lg" />
        </div>
      ) : error ? (
        <div className="flex flex-col items-center justify-center h-screen">
          <h1 className="text-red-500">Error: {error}</h1>
        </div>
      ) : (
        <h1>You&apos;re not supposed to be here!</h1>
      )}
    </main>
  );
}
