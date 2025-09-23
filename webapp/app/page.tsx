"use client";
import Image from "next/image";
import { useEffect, useState } from "react";
import { Spinner, Card, CardBody } from "@nextui-org/react";

export default function Home() {
  const [loading, setLoading] = useState(true);

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
      if (params[0] === "dashboard") {
        window.location.href = `/dashboard?token=${token}`;
      }
      if (params[0] === "dragselector" && token) {
        window.location.href = `/dragselector?event_id=${token}`;
      }
      if (params[0] === "confirm") {
        window.location.href = `/confirm?event_id=${token}`;
      }
    } else {
      // No start param, show the page after loading
      setTimeout(() => setLoading(false), 1000);
    }
  }, []);

  // Initialize page data
  useEffect(() => {
    const initializePage = async () => {
      try {
        // Wait for all critical data to be ready
        await Promise.all([
          // Wait for DOM to be ready
          new Promise(resolve => {
            if (document.readyState === 'complete') {
              resolve(true);
            } else {
              window.addEventListener('load', () => resolve(true));
            }
          }),
          // Wait for fonts to load
          new Promise(resolve => {
            if (document.fonts) { 
              document.fonts.ready.then(() => resolve(true));
            } else {
              setTimeout(() => resolve(true), 100);
            }
          })
        ]);

        // Small delay to ensure smooth rendering
        setTimeout(() => {
          setLoading(false);
        }, 300);
      } catch (error) {
        console.error('Page initialization error:', error);
        // Show page anyway after timeout
        setTimeout(() => {
          setLoading(false);
        }, 1000);
      }
    };

    initializePage();
  }, []);

  // Loading state with smooth transitions
  if (loading) {
    return (
      <div className="transition-opacity duration-500 opacity-100">
        <main className="font-body bg-black min-h-screen flex items-center justify-center p-4">
          <Card className="bg-dark-secondary border border-border-primary shadow-lg">
            <CardBody className="flex items-center justify-center p-8">
              <Spinner size="lg" color="primary" />
              <p className="text-text-primary mt-4 text-center font-body">Loading MeetWhenAh...</p>
              <p className="text-text-tertiary mt-2 text-sm text-center font-caption">
                Preparing your experience
              </p>
            </CardBody>
          </Card>
        </main>
      </div>
    );
  }

  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24 transition-opacity duration-500 opacity-100">
      <h1>You&apos;re not supposed to be here!</h1>
    </main>
  );
}
