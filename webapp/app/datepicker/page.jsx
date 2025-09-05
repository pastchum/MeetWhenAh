"use client";
import EventForm from "@/components/datepicker/EventForm";
import EventDateSelector from "@/components/datepicker/EventDateSelector";
import ReviewSubmit from "@/components/datepicker/ReviewSubmit";
import { useState, useEffect, useCallback, useMemo } from "react";
import { useTelegramViewport } from "@/hooks/useTelegramViewport";
import { Card, CardBody } from "@nextui-org/react";
import { v4 as uuidv4 } from "uuid";

export default function DatePicker() {
  // Telegram viewport setup
  useTelegramViewport();

  const [data, setData] = useState({
    token: "",
    event_id: uuidv4(),
    event_name: "",
    event_details: "",
    start: null,
    end: null,
    creator: "",
  });

  const [currentComponent, setCurrentComponent] = useState(0);
  const [tokenOwner, setTokenOwner] = useState("");

  const nextComponent = (newData) => {
    console.log("next component", newData);
    if (newData) {
      setData((prevData) => ({ ...prevData, ...newData }));
      setCurrentComponent((prev) => prev + 1);
    }
  };

  const prevComponent = () => {
    console.log("prev component");
    setCurrentComponent((prev) => prev - 1);
  };

  const [tg, setTg] = useState(null);

  useEffect(() => {
    if (typeof window !== "undefined" && window.Telegram?.WebApp) {
      setTg(window.Telegram.WebApp);
    }
  }, []);

  useEffect(() => {
    if (tg) {
      try {
        tg.ready();
        tg.expand();
      } catch (error) {
        console.warn("Telegram WebApp error:", error);
      }
    }
  }, [tg]);

  useEffect(() => {
    if (tg) {
      setData((prevData) => ({
        ...prevData,
        creator: tg.initDataUnsafe.user.id,
      }));
    }
  }, [tg]);

  const [token, setToken] = useState(null);
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const url_token = urlParams.get("token");
    if (url_token) {
      setToken(url_token);
    }
  }, []);

  useEffect(() => {
    setData((prevData) => ({ ...prevData, token: token }));
  }, [token]);

  const fetchCtx = useCallback(async () => {
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

  useEffect(() => {
    const fetchData = async () => {
      console.log(token);
      const ctx = await fetchCtx();
      if (ctx) {
        setTokenOwner(ctx.tele_id);
      }
    };
    fetchData();
  }, [token, fetchCtx, tg]);

  const telegramId = tg?.initDataUnsafe?.user?.id;

  const isOwner = useMemo(() => {
    if (telegramId == null || tokenOwner == null) return false;
    return String(tokenOwner).trim() === String(telegramId).trim();
  }, [telegramId, tokenOwner]);

  return (
    <main className="minecraft-font bg-black min-h-screen flex flex-col items-center justify-start p-4">
      <div className="w-full max-w-md mb-6 text-center">
        <h1 
          className="font-semibold text-3xl cursor-pointer hover:opacity-80 transition-opacity"
          onClick={() => {
            // Get token from URL and pass it back to dashboard
            const urlParams = new URLSearchParams(window.location.search);
            const token = urlParams.get('token');
            const dashboardUrl = token ? `/dashboard?token=${token}` : '/dashboard';
            window.location.href = dashboardUrl;
          }}
        >
          <span className="text-white">MeetWhen</span><span className="text-[#c44545]">?</span>
        </h1>
      </div>

      <div className="w-full max-w-md">
        {currentComponent === 0 && (
          <Card className="bg-[#0a0a0a] border border-white shadow-lg">
            <CardBody className="p-6">
              <EventForm
                nextComponent={nextComponent}
                data={data}
                setData={setData}
              />
            </CardBody>
          </Card>
        )}
        {currentComponent === 1 && (
          <Card className="bg-[#0a0a0a] border border-white shadow-lg">
            <CardBody className="p-6">
              <EventDateSelector
                nextComponent={nextComponent}
                prevComponent={prevComponent}
                data={data}
                setData={setData}
              />
            </CardBody>
          </Card>
        )}
        {currentComponent === 2 && (
          <Card className="bg-[#0a0a0a] border border-white shadow-lg">
            <CardBody className="p-6">
              <ReviewSubmit
                data={data}
                prevComponent={prevComponent}
                isOwner={isOwner}
              />
            </CardBody>
          </Card>
        )}
      </div>
    </main>
  );
}
