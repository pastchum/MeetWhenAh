"use client";
import Image from "next/image";
import { useEffect } from "react";

export default function Home() {
  useEffect(() => {
    const tg = window.Telegram.WebApp;
    const startParam = tg.initDataUnsafe.start_param;
    if (startParam) {
      const params = startParam.split("=");
      const token = params[1];
      if (params[0] === "datepicker") {
        window.location.href = `/datepicker?token=${token}`;
      }
      if (params[0] === "share") {
        window.location.href = `/share?token=${token}`;
      }
      if (params[0] === "dragselector" && token) {
        window.location.href = `/dragselector?event_id=${token}`;
      }
      if (params[0] === "confirm") {
        window.location.href = `/confirm?event_id=${token}`;
      }
    }
  }, []);

  // #TODO: add a loading screen that we can use whenever the app is loading
  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24">
      <h1>You&apos;re not supposed to be here!</h1>
    </main>
  );
}
