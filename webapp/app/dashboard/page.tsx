"use client";
import React, { useState, useEffect, useRef } from "react";
import { Button, Spinner } from "@nextui-org/react";
import { 
  CalendarDaysIcon, 
  UserPlusIcon, 
  ShareIcon, 
  CheckCircleIcon,
  ArrowRightIcon
} from "@heroicons/react/24/outline";
import { useTelegramViewport } from "@/hooks/useTelegramViewport";
import { useOverlay } from "@/hooks/useOverlay";
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
  const { showOverlay } = useOverlay();
  const [isPageReady, setIsPageReady] = useState(false);

  // Token management
  const [token, setToken] = useState<string | null>(null);

  // Telegram WebApp setup
  const [tg, setTg] = useState<any>(null);
  const [hasTelegramContext, setHasTelegramContext] = useState(false);
  const [teleId, setTeleId] = useState<string>("");
  const [username, setUsername] = useState<string>("");
  const [userUuid, setUserUuid] = useState<string>("");

  // Show initial page loading overlay
  useEffect(() => {
    showOverlay(
      <div className="fixed inset-0 bg-black flex items-center justify-center z-[9999]">
        <div className="bg-dark-secondary p-6 rounded-lg border border-border-primary">
          <div className="flex flex-col items-center">
            <Spinner size="lg" color="primary" />
            <p className="text-text-primary mt-4 text-center">Loading Dashboard...</p>
            <p className="text-text-tertiary mt-2 text-sm text-center">
              Getting everything ready for you
            </p>
          </div>
        </div>
      </div>,
      {
        fadeInDuration: 200,
        displayDuration: 999999999, // Keep showing until we hide it
        fadeOutDuration: 400
      }
    );
  }, [showOverlay]);

  // Check when page is ready (DOM loaded + basic setup complete)
  useEffect(() => {
    const checkPageReady = () => {
      // Wait for DOM to be fully loaded and a short delay for React to finish rendering
      if (document.readyState === 'complete') {
        setTimeout(() => {
          setIsPageReady(true);
        }, 500); // Small delay to ensure smooth rendering
      }
    };

    if (document.readyState === 'complete') {
      checkPageReady();
    } else {
      window.addEventListener('load', checkPageReady);
      return () => window.removeEventListener('load', checkPageReady);
    }
  }, []);

  // Hide overlay when page is ready
  useEffect(() => {
    if (isPageReady) {
      // Hide overlay with a transparent one
      showOverlay(
        <div className="fixed inset-0 bg-transparent pointer-events-none z-[9999]"></div>,
        {
          fadeInDuration: 0,
          displayDuration: 0,
          fadeOutDuration: 400
        }
      );
    }
  }, [isPageReady, showOverlay]);

  // Token initialization - ensure dashboard always has a token
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const urlToken = urlParams.get('token');
    
    if (urlToken) {
      // Use existing token from URL
      setToken(urlToken);
      console.log('[Dashboard] Using existing token from URL:', urlToken);
    } else {
      // Generate new token and update URL
      const newToken = crypto.randomUUID();
      setToken(newToken);
      
      // Update URL with new token without page reload
      const newUrl = new URL(window.location.href);
      newUrl.searchParams.set('token', newToken);
      window.history.replaceState({}, '', newUrl.toString());
      
      console.log('[Dashboard] Generated new token and updated URL:', newToken);
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
    console.log('[Dashboard] User UUID useEffect triggered:', { teleId });
    
    if (!teleId) {
      console.log('[Dashboard] No teleId available');
      return;
    }
    
    const fetchUserUuidFromTeleId = async () => {
      console.log('[Dashboard] Fetching user data for teleId:', teleId.toString());
      
      const userData = await fetchUserDataFromId(teleId.toString());
      console.log('[Dashboard] User data response:', userData);
      
      if (userData) {
        setUserUuid(userData.uuid);
        setUsername(userData.tele_user);
        console.log('[Dashboard] Set user data:', {
          uuid: userData.uuid,
          username: userData.tele_user,
          teleId: userData.tele_id
        });
      } else {
        console.log('[Dashboard] No user data found, creating new user');
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
            console.log('[Dashboard] Created new user:', newUser);
          }
        } catch (error) {
          console.error('[Dashboard] Error creating user:', error);
        }
      }
    };
    
    fetchUserUuidFromTeleId();
  }, [teleId]);

  const handleActionClick = (route: string) => {
    console.log(`🎯 Dashboard action clicked: ${route}`, {
      timestamp: new Date().toISOString(),
      hasTelegramContext,
      user: tg?.initDataUnsafe?.user,
      platform: tg?.platform,
      teleId,
      username,
      userUuid,
      currentUrl: window.location.href,
      targetRoute: route
    });
    
    // Add token to route (token should always exist)
    let targetRoute = route;
    if (token) {
      targetRoute = route.includes('?') ? `${route}&token=${token}` : `${route}?token=${token}`;
    }
    
    console.log(`🌐 Navigating to: ${targetRoute}`);
    
    // Simple navigation - let destination page handle loading
    window.location.href = targetRoute;
  };

  const handleShareClick = () => {
    console.log('🎯 Dashboard share action clicked', {
      timestamp: new Date().toISOString(),
      hasTelegramContext,
      user: tg?.initDataUnsafe?.user,
      platform: tg?.platform,
      teleId,
      username,
      userUuid,
      currentUrl: window.location.href
    });
    
    if (!hasTelegramContext) {
      console.warn('⚠️ Share clicked without Telegram context');
      alert("Share functionality requires being accessed from a chat. Please open the bot from a chat.");
      return;
    }
    
    if (!token) {
      console.warn('⚠️ No token available for sharing');
      alert("Share functionality requires being accessed from a chat. Please open the bot from a chat.");
      return;
    }
    
    const shareUrl = `/share?token=${token}`;
    console.log(`🌐 Share: Navigating to ${shareUrl}`);
    
    // Simple navigation - let destination page handle loading
    window.location.href = shareUrl;
  };

  const handleEventAction = (eventId: string, action: string) => {
    console.log(`🎯 Dashboard event action clicked: ${action}`, {
      timestamp: new Date().toISOString(),
      eventId,
      action,
      hasTelegramContext,
      user: tg?.initDataUnsafe?.user,
      platform: tg?.platform,
      teleId,
      username,
      userUuid
    });
    
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

  return (
    <div 
      className="flex flex-col w-full bg-black min-h-screen"
      style={{ 
        height: `${viewport.totalHeight}px`,
        transform: 'translateZ(0)'
      }}
    >
      {/* Fixed Header Section */}
      <div className="flex-shrink-0 p-4 bg-dark-secondary border-b border-border-primary">
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
                console.log('📱 Create Event ActionCard clicked - calling handleActionClick("/datepicker")');
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
                console.log('📱 Share Event ActionCard clicked - calling handleShareClick()');
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
