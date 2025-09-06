"use client";
import React, { useState, useEffect, useRef } from "react";
import { Button, Spinner, Card, CardBody } from "@nextui-org/react";
import { 
  CalendarDaysIcon, 
  UserPlusIcon, 
  ShareIcon, 
  CheckCircleIcon,
  ArrowRightIcon
} from "@heroicons/react/24/outline";
import { useTelegramViewport } from "@/hooks/useTelegramViewport";
import { fetchUserDataFromId, addUserToDatabase } from "@/routes/user_routes";
import { useRouter } from "next/navigation";
import ActionCard from "@/components/dashboard/ActionCard";

// Mock data for recent events (will be replaced with real data later)
const mockEvents = [
  {
    id: "1",
    name: "Team Meeting",
    start_date: "2025-09-03",
    start_hour: 14,
    end_date: "2025-09-03", 
    end_hour: 15,
    timezone: "UTC+2",
    role: "creator" // or "participant"
  },
  {
    id: "2", 
    name: "Coffee Chat",
    start_date: "2025-09-04",
    start_hour: 10,
    end_date: "2025-09-04",
    end_hour: 11,
    timezone: "UTC+2",
    role: "participant"
  }
];

export default function Dashboard() {
  // Get viewport dimensions from Telegram Web App
  const viewport = useTelegramViewport();
  const [loading, setLoading] = useState(true);

  // Token management
  const [token, setToken] = useState<string | null>(null);

  // Telegram WebApp setup
  const [tg, setTg] = useState<any>(null);
  const [hasTelegramContext, setHasTelegramContext] = useState(false);
  const [teleId, setTeleId] = useState<string>("");
  const [username, setUsername] = useState<string>("");
  const [userUuid, setUserUuid] = useState<string>("");

  // Initialize dashboard data
  useEffect(() => {
    const initializeDashboard = async () => {
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
        console.error('Dashboard initialization error:', error);
        // Show dashboard anyway after timeout
        setTimeout(() => {
          setLoading(false);
        }, 1000);
      }
    };

    initializeDashboard();
  }, []);

  // Token initialization - ensure dashboard always has a token
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const urlToken = urlParams.get('token');
    
    if (urlToken) {
      // Use existing token from URL
      setToken(urlToken);
    } else {
      // Generate new token and update URL
      const newToken = crypto.randomUUID();
      setToken(newToken);
      
      // Update URL with new token without page reload
      const newUrl = new URL(window.location.href);
      newUrl.searchParams.set('token', newToken);
      window.history.replaceState({}, '', newUrl.toString());
      
    }
  }, []);

  useEffect(() => {
    if (typeof window !== "undefined" && window.Telegram?.WebApp) {
      setTg(window.Telegram.WebApp);
      // Check if we have Telegram context (user data)
      // For WebApp buttons, we have user data but no start_param
      const hasUser = window.Telegram.WebApp.initDataUnsafe.user;
      setHasTelegramContext(!!hasUser);
      
      // Comprehensive logging for dashboard access
      const logData = {
        timestamp: new Date().toISOString(),
        hasUser: !!hasUser,
        user: hasUser,
        isWebApp: window.Telegram.WebApp.isExpanded,
        platform: window.Telegram.WebApp.platform,
        version: window.Telegram.WebApp.version,
        initData: window.Telegram.WebApp.initData,
        initDataUnsafe: window.Telegram.WebApp.initDataUnsafe,
        viewportHeight: window.Telegram.WebApp.viewportHeight,
        isExpanded: window.Telegram.WebApp.isExpanded,
        themeParams: window.Telegram.WebApp.themeParams,
        colorScheme: window.Telegram.WebApp.colorScheme
      };
      
      console.log('🚀 Dashboard accessed - Telegram context:', logData);
      
      // Extract tele_id from Telegram user data
      if (hasUser) {
        const telegramUser = window.Telegram.WebApp.initDataUnsafe.user;
        if (telegramUser && telegramUser.id) {
          setTeleId(telegramUser.id.toString());
          setUsername(telegramUser.username || telegramUser.first_name || "");
          console.log('📱 Extracted Telegram user data:', {
            teleId: telegramUser.id.toString(),
            username: telegramUser.username || telegramUser.first_name,
            firstName: telegramUser.first_name,
            lastName: telegramUser.last_name
          });
        }
      }
    } else {
      console.log('🚀 Dashboard accessed - No Telegram context (direct web access)');
    }
  }, []);

  useEffect(() => {
    if (tg) {
      try {
        tg.ready();
        tg.expand();
      } catch (error) {
        console.warn('Telegram WebApp error:', error);
      }
    }
  }, [tg]);

  // Fetch user UUID from tele_id
  useEffect(() => {
    if (!teleId) {
      return;
    }
    
    const fetchUserUuidFromTeleId = async () => {
      const userData = await fetchUserDataFromId(teleId.toString());
      
      if (userData) {
        setUserUuid(userData.uuid);
        setUsername(userData.tele_user);
      } else {
        // Create new user if not found
        const newUserData = {
          tele_id: teleId,
          tele_user: username || "",
        };
        
        try {
          const newUser = await addUserToDatabase(newUserData);
          if (newUser) {
            setUserUuid(newUser.uuid);
            setUsername(newUser.tele_user);
            setTeleId(newUser.tele_id);
          }
        } catch (error) {
          console.error('[Dashboard] Error creating user:', error);
        }
      }
    };
    
    fetchUserUuidFromTeleId();
  }, [teleId, username]);

  const handleActionClick = (route: string) => {
    // Add token to route (token should always exist)
    let targetRoute = route;
    if (token) {
      targetRoute = route.includes('?') ? `${route}&token=${token}` : `${route}?token=${token}`;
    }
    
    // Simple navigation - let destination page handle loading
    window.location.href = targetRoute;
  };

  const handleShareClick = () => {
    if (!hasTelegramContext) {
      alert("Share functionality requires being accessed from a chat. Please open the bot from a chat.");
      return;
    }
    
    if (!token) {
      alert("Share functionality requires being accessed from a chat. Please open the bot from a chat.");
      return;
    }
    
    const shareUrl = `/share?token=${token}`;
    
    // Simple navigation - let destination page handle loading
    window.location.href = shareUrl;
  };

  const handleEventAction = (eventId: string, action: string) => {
    if (action === "confirm") {
      window.location.href = `/confirm?event_id=${eventId}`;
    } else if (action === "availability") {
      window.location.href = `/dragselector?event_id=${eventId}`;
    }
  };

  const formatEventDate = (dateStr: string, hour: number) => {
    const date = new Date(dateStr);
    return `${date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })} at ${hour}:00`;
  };

  // Loading state with smooth transitions
  if (loading) {
    return (
      <div className="transition-opacity duration-500 opacity-100">
        <main className="minecraft-font bg-black min-h-screen flex items-center justify-center p-4">
          <Card className="bg-dark-secondary border border-border-primary shadow-lg">
            <CardBody className="flex items-center justify-center p-8">
              <Spinner size="lg" color="primary" />
              <p className="text-text-primary mt-4 text-center">Loading Dashboard...</p>
              <p className="text-text-tertiary mt-2 text-sm text-center">
                Getting everything ready for you
              </p>
            </CardBody>
          </Card>
        </main>
      </div>
    );
  }

  return (
    <div 
      className="flex flex-col w-full bg-black min-h-screen transition-opacity duration-500 opacity-100"
      style={{ 
        height: `${viewport.totalHeight}px`,
        transform: 'translateZ(0)'
      }}
    >
      {/* Fixed Header Section */}
      <div className="flex-shrink-0 p-4 bg-dark-secondary">
        <div className="text-center">
          <h1 className="font-semibold text-3xl mb-2">
            <span className="text-text-primary">MeetWhen</span><span className="text-[#c44545]">?</span>
          </h1>
          <p className="text-sm text-text-tertiary">
            Plan, join, and coordinate events with ease
          </p>
        </div>
      </div>

      {/* Main Content - Scrollable */}
      <div className="flex-1 px-4 py-6 overflow-y-auto">
        {/* Action Cards Grid */}
        <div className="mb-8">
          <h2 className="text-xl font-semibold mb-4 text-text-primary">Quick Actions</h2>
          <div className="grid grid-cols-1 gap-4">
            <ActionCard
              icon={<CalendarDaysIcon />}
              title="Create Event"
              description="Make a new event"
              iconBgColor="bg-blue-500/20"
              iconColor="text-blue-400"
              onClick={() => {
                handleActionClick('/datepicker');
              }}
            />
            <ActionCard
              icon={<ShareIcon />}
              title="Manage Events"
              description="Share and confirm event timings"
              iconBgColor="bg-purple-500/20"
              iconColor="text-purple-400"
              onClick={() => {
                handleShareClick();
              }}
            />
            
            {/* <ActionCard
              icon={<UserPlusIcon />}
              title="Join Event"
              description="Update your availability for an event"
              iconBgColor="bg-green-500/20"
              iconColor="text-green-400"
              onClick={() => {
                console.log('📱 Join Event ActionCard clicked - showing not implemented overlay');
                alert('Join Event feature is not yet implemented. Please use the bot commands for now.');
              }}
            /> */}
          </div>
        </div>

        {/* Recent Events Section */}
        {/* <div className="mb-6">
          <h2 className="text-xl font-semibold mb-4 text-text-primary">Recent Events</h2>
          <div className="space-y-3">
            {mockEvents.map((event) => (
              <div key={event.id} className="bg-dark-secondary border border-border-primary rounded-lg p-4">
                  <div className="flex justify-between items-start mb-3">
                    <div>
                      <h3 className="font-semibold text-text-primary">{event.name}</h3>
                      <p className="text-sm text-text-tertiary">
                        {formatEventDate(event.start_date, event.start_hour)} - {formatEventDate(event.end_date, event.end_hour)}
                      </p>
                      <p className="text-xs text-text-tertiary">{event.timezone}</p>
                    </div>
                    <span className={`px-2 py-1 text-xs rounded-full ${
                      event.role === 'creator' 
                        ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30' 
                        : 'bg-green-500/20 text-green-400 border border-green-500/30'
                    }`}>
                      {event.role === 'creator' ? 'Creator' : 'Participant'}
                    </span>
                  </div>
                  
                  <div className="flex space-x-2">
                    {event.role === 'creator' && (
                      <Button
                        size="sm"
                        variant="bordered"
                        className="border-[#a83838] text-[#a83838] hover:bg-[#a83838] hover:text-white"
                        onClick={() => {
                          console.log(`📱 Mock event "${event.name}" Confirm Timing button clicked - calling handleEventAction("${event.id}", "confirm")`);
                          handleEventAction(event.id, 'confirm');
                        }}
                      >
                        Confirm Timing
                      </Button>
                    )}
                    <Button
                      size="sm"
                      variant="bordered"
                      className="border-[#a83838] text-[#a83838] hover:bg-[#a83838] hover:text-white"
                      onClick={() => {
                        console.log(`📱 Mock event "${event.name}" Set Availability button clicked - calling handleEventAction("${event.id}", "availability")`);
                        handleEventAction(event.id, 'availability');
                      }}
                    >
                      Set Availability
                    </Button>
                  </div>
              </div>
            ))}
          </div>
        </div> */}
      </div>

    </div>
  );
}
