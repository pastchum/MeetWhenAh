"use client";
import Image from "next/image";
import { useEffect } from "react";

export default function Home() {
  useEffect(() => {
    const tg = window.Telegram.WebApp;
    const startParam = tg.initDataUnsafe.start_param;
    if (startParam) {
      const params = startParam.split("=");
      const eventId = params[1];
      if (params[0] === "dragselector" && eventId) {
        window.location.href = `/dragselector?event_id=${eventId}`;
      }
    }
  }, []);
  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24">
      <h1>You&apos;re not supposed to be here!</h1>
    </main>
  );
}
