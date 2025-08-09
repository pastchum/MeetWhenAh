import { useState, useEffect } from 'react';

interface TelegramViewport {
  totalHeight: number;
  platform: string;
  isExpanded: boolean;
  viewportHeight: number;
  safeAreaInsets: {
    top: number;
    right: number;
    bottom: number;
    left: number;
  };
}

export function useTelegramViewport(): TelegramViewport {
  const [viewport, setViewport] = useState<TelegramViewport>({
    totalHeight: 0,
    platform: 'unknown',
    isExpanded: false,
    viewportHeight: 0,
    safeAreaInsets: {
      top: 0,
      right: 0,
      bottom: 0,
      left: 0,
    },
  });

  useEffect(() => {
    const updateViewport = () => {
      if (typeof window !== 'undefined' && window.Telegram?.WebApp) {
        const tg = window.Telegram.WebApp;
        
        // Get viewport height from Telegram
        const viewportHeight = tg.viewportHeight || window.innerHeight;
        
        // Get platform information
        const platform = tg.platform || 'unknown';
        
        // Check if viewport is expanded
        const isExpanded = tg.isExpanded || false;
        
        // Get safe area insets for proper padding
        const safeAreaInsets = {
          top: (tg as any).safeAreaInsets?.top || 0,
          right: (tg as any).safeAreaInsets?.right || 0,
          bottom: (tg as any).safeAreaInsets?.bottom || 0,
          left: (tg as any).safeAreaInsets?.left || 0,
        };

        // Calculate total height with padding adjustments
        // This accounts for Telegram's UI elements and safe areas
        let totalHeight = viewportHeight;
        
        // Adjust for different platforms
        if (platform === 'ios') {
          // iOS has more UI elements, reduce height slightly
          totalHeight = viewportHeight - safeAreaInsets.top - safeAreaInsets.bottom - 20;
        } else if (platform === 'android') {
          // Android has status bar and navigation bar
          totalHeight = viewportHeight - safeAreaInsets.top - safeAreaInsets.bottom - 16;
        } else {
          // Web/desktop - minimal adjustments
          totalHeight = viewportHeight - 10;
        }

        // Ensure minimum height
        totalHeight = Math.max(totalHeight, 400);

        setViewport({
          totalHeight,
          platform,
          isExpanded,
          viewportHeight,
          safeAreaInsets,
        });

        // Expand viewport to use full height
        if (!isExpanded) {
          try {
            tg.expand();
          } catch (error) {
            console.warn('Failed to expand Telegram Web App viewport:', error);
          }
        }

        // Disable vertical swipes to prevent scrolling issues
        try {
          tg.disableVerticalSwipes();
        } catch (error) {
          console.warn('Failed to disable vertical swipes:', error);
        }
      }
    };

    // Initial update
    updateViewport();

    // Update on window resize
    window.addEventListener('resize', updateViewport);

            // Update when Telegram Web App viewport changes
        if (typeof window !== 'undefined' && window.Telegram?.WebApp) {
          const tg = window.Telegram.WebApp;
          
          // Listen for viewport changes
          try {
            tg.onEvent('viewportChanged', updateViewport);
            tg.onEvent('themeChanged', updateViewport);
          } catch (error) {
            console.warn('Failed to add Telegram Web App event listeners:', error);
          }
        }

    return () => {
      window.removeEventListener('resize', updateViewport);
      
      if (typeof window !== 'undefined' && window.Telegram?.WebApp) {
        const tg = window.Telegram.WebApp;
        try {
          tg.offEvent('viewportChanged', updateViewport);
          tg.offEvent('themeChanged', updateViewport);
        } catch (error) {
          console.warn('Failed to remove Telegram Web App event listeners:', error);
        }
      }
    };
  }, []);

  return viewport;
} 