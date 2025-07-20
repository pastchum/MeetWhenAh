"use client";
import { useLayoutEffect, useState } from 'react';

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

  useLayoutEffect(() => {
    const tg = window.Telegram?.WebApp;
    
    function calculateDimensions() {
      console.log('[TelegramViewport] Calculating dimensions...');
      
      if (!tg) {
        // Fallback for non-Telegram environment
        const fallbackHeight = window.innerHeight;
        const headerHeight = Math.round(fallbackHeight * 0.15);
        const instructionsHeight = Math.round(fallbackHeight * 0.05);
        const selectedTimesHeight = Math.round(fallbackHeight * 0.10);
        const calendarHeight = fallbackHeight - headerHeight - instructionsHeight - selectedTimesHeight;

        const fallbackDimensions = {
          totalHeight: fallbackHeight,
          headerHeight,
          instructionsHeight,
          calendarHeight,
          selectedTimesHeight,
          isTelegramWebApp: false,
          platform: 'unknown'
        };

        console.log('[TelegramViewport] Fallback dimensions:', fallbackDimensions);
        setDimensions(fallbackDimensions);
        return;
      }

      // Use viewportStableHeight for iOS (more reliable)
      const view = tg.viewportStableHeight ?? tg.viewportHeight;
      const insets = (tg as any).contentSafeArea || { top: 0, bottom: 0 };
      const usable = view - insets.top - insets.bottom;

      // "Mind the gap" – difference between what Telegram reports and the real DOM viewport
      const gap = Math.max(0, window.innerHeight - usable);
      const finalHeight = usable - gap;

      console.log('[TelegramViewport] Telegram calculations:', {
        platform: tg.platform,
        viewportHeight: tg.viewportHeight,
        viewportStableHeight: tg.viewportStableHeight,
        view,
        insets,
        usable,
        gap,
        finalHeight,
        windowInnerHeight: window.innerHeight
      });

      // Calculate section heights based on final height
      const headerHeight = Math.round(finalHeight * 0.15);
      const instructionsHeight = Math.round(finalHeight * 0.05);
      const selectedTimesHeight = Math.round(finalHeight * 0.10);
      const calendarHeight = finalHeight - headerHeight - instructionsHeight - selectedTimesHeight;

      const newDimensions = {
        totalHeight: finalHeight,
        headerHeight,
        instructionsHeight,
        calendarHeight,
        selectedTimesHeight,
        isTelegramWebApp: true,
        platform: tg.platform || 'unknown'
      };

      console.log('[TelegramViewport] Final dimensions:', newDimensions);
      setDimensions(newDimensions);
    }

    // Initial calculation
    calculateDimensions();

    // Set up event listeners
    if (tg) {
      tg.onEvent('viewportChanged', calculateDimensions);
      // Note: contentSafeAreaChanged event may not be available in all Telegram Web App versions
      // We'll rely on viewportChanged for now
      
      return () => {
        tg.offEvent('viewportChanged', calculateDimensions);
      };
    } else {
      // Fallback for non-Telegram environment
      const handleResize = () => {
        console.log('[TelegramViewport] Window resize detected');
        calculateDimensions();
      };

      window.addEventListener('resize', handleResize);
      return () => window.removeEventListener('resize', handleResize);
    }
  }, []);

  return dimensions;
} 