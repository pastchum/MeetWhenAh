"use client";
import { useState, useEffect, useCallback } from 'react';

interface ViewportDimensions {
  totalHeight: number;
  headerHeight: number;
  instructionsHeight: number;
  calendarHeight: number;
  selectedTimesHeight: number;
  isTelegramWebApp: boolean;
  platform: string;
}

export function useTelegramViewport(): ViewportDimensions {
  const [dimensions, setDimensions] = useState<ViewportDimensions>({
    totalHeight: 600, // Fallback height
    headerHeight: 90, // 15% of 600
    instructionsHeight: 30, // 5% of 600
    calendarHeight: 420, // 70% of 600
    selectedTimesHeight: 60, // 10% of 600
    isTelegramWebApp: false,
    platform: 'unknown'
  });

  const calculateDimensions = useCallback((viewportHeight: number) => {
    console.log('[TelegramViewport] Calculating dimensions for height:', viewportHeight);
    
    const headerHeight = Math.round(viewportHeight * 0.15);
    const instructionsHeight = Math.round(viewportHeight * 0.05);
    const selectedTimesHeight = Math.round(viewportHeight * 0.10);
    const calendarHeight = viewportHeight - headerHeight - instructionsHeight - selectedTimesHeight;

    const newDimensions = {
      totalHeight: viewportHeight,
      headerHeight,
      instructionsHeight,
      calendarHeight,
      selectedTimesHeight,
      isTelegramWebApp: true,
      platform: window.Telegram?.WebApp?.platform || 'unknown'
    };

    console.log('[TelegramViewport] Calculated dimensions:', newDimensions);
    return newDimensions;
  }, []);

  useEffect(() => {
    const initializeViewport = () => {
      console.log('[TelegramViewport] Initializing viewport...');
      
      // Check if we're in Telegram Web App
      if (window.Telegram?.WebApp) {
        const webApp = window.Telegram.WebApp;
        console.log('[TelegramViewport] Telegram Web App detected:', {
          platform: webApp.platform,
          viewportHeight: webApp.viewportHeight,
          viewportStableHeight: webApp.viewportStableHeight,
          isExpanded: webApp.isExpanded
        });

        // Use viewportStableHeight for iOS (more reliable)
        const viewportHeight = webApp.platform === 'ios' 
          ? webApp.viewportStableHeight 
          : webApp.viewportHeight;

        const newDimensions = calculateDimensions(viewportHeight);
        setDimensions(newDimensions);

        // Listen for viewport changes (keyboard, orientation, etc.)
        const handleViewportChange = () => {
          console.log('[TelegramViewport] Viewport change detected');
          const updatedHeight = webApp.platform === 'ios' 
            ? webApp.viewportStableHeight 
            : webApp.viewportHeight;
          
          const updatedDimensions = calculateDimensions(updatedHeight);
          setDimensions(updatedDimensions);
        };

        // Set up viewport change listener
        webApp.onEvent('viewportChanged', handleViewportChange);
        
        // Also listen for window resize as fallback
        window.addEventListener('resize', handleViewportChange);

        return () => {
          webApp.offEvent('viewportChanged', handleViewportChange);
          window.removeEventListener('resize', handleViewportChange);
        };
      } else {
        console.log('[TelegramViewport] Not in Telegram Web App, using fallback dimensions');
        // CSS fallback - use viewport height
        const fallbackHeight = window.innerHeight;
        const fallbackDimensions = calculateDimensions(fallbackHeight);
        fallbackDimensions.isTelegramWebApp = false;
        setDimensions(fallbackDimensions);

        // Listen for window resize
        const handleResize = () => {
          console.log('[TelegramViewport] Window resize detected');
          const newHeight = window.innerHeight;
          const newDimensions = calculateDimensions(newHeight);
          newDimensions.isTelegramWebApp = false;
          setDimensions(newDimensions);
        };

        window.addEventListener('resize', handleResize);
        return () => window.removeEventListener('resize', handleResize);
      }
    };

    // Initialize on mount
    initializeViewport();
  }, [calculateDimensions]);

  return dimensions;
} 