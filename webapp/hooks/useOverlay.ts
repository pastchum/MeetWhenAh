import React, { useContext, createContext, ReactNode, useState, useCallback, useEffect, useRef } from 'react';
import { usePathname } from 'next/navigation';

interface OverlayOptions {
  fadeInDuration?: number;
  displayDuration?: number;
  fadeOutDuration?: number;
}

interface OverlayContextType {
  showOverlay: (content: ReactNode, options?: OverlayOptions) => void;
}

const OverlayContext = createContext<OverlayContextType | null>(null);

export const useOverlay = () => {
  const context = useContext(OverlayContext);
  if (!context) {
    throw new Error('useOverlay must be used within an OverlayProvider');
  }
  return context;
};

interface OverlayProviderProps {
  children: ReactNode;
}

export const OverlayProvider: React.FC<OverlayProviderProps> = ({ children }) => {
  const [overlayContent, setOverlayContent] = useState<ReactNode | null>(null);
  const [isVisible, setIsVisible] = useState(false);
  const pathname = usePathname();
  const currentPageRef = useRef<string>('');
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  // Track current page
  useEffect(() => {
    currentPageRef.current = pathname;
  }, [pathname]);

  // Clear overlay when page changes
  useEffect(() => {
    if (overlayContent) {
      clearOverlay();
    }
  }, [pathname]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (timerRef.current) {
        clearTimeout(timerRef.current);
        timerRef.current = null;
      }
    };
  }, []);

  const clearOverlay = useCallback(() => {
    if (timerRef.current) {
      clearTimeout(timerRef.current);
      timerRef.current = null;
    }
    setIsVisible(false);
    // Don't immediately clear content - let fade out complete
  }, []);

  const showOverlay = useCallback((content: ReactNode, options?: OverlayOptions) => {
    // Clear any existing overlay and wait for it to complete
    if (overlayContent || isVisible) {
      clearOverlay();
      
      // Wait for fade out to complete before showing new overlay
      setTimeout(() => {
        setOverlayContent(null);
        
        // Additional delay for iframe context to ensure DOM stability
        setTimeout(() => {
          // Now show the new overlay
          setOverlayContent(content);
          setIsVisible(false);
          
          // Force multiple reflows to ensure iframe DOM is stable
          requestAnimationFrame(() => {
            // Force multiple layout calculations for iframe stability
            document.body.offsetHeight;
            document.documentElement.offsetHeight;
            
            // Additional frame wait for iframe context
            requestAnimationFrame(() => {
              // Now trigger visible state for smooth transition
              setIsVisible(true);
            });
          });
          
          // Set up auto-hide timer
          const fadeInDuration = options?.fadeInDuration || 500;
          const displayDuration = options?.displayDuration || 1000;
          const fadeOutDuration = options?.fadeOutDuration || 500;
          
          timerRef.current = setTimeout(() => {
            setIsVisible(false);
            // Remove from DOM after fade out completes
            setTimeout(() => {
              setOverlayContent(null);
            }, fadeOutDuration);
          }, fadeInDuration + displayDuration);
        }, 50); // Additional iframe stability delay
      }, 200); // Wait for fade out to complete
    } else {
      // No existing overlay, show immediately
      setOverlayContent(content);
      setIsVisible(false);
      
      // Force multiple reflows to ensure iframe DOM is stable
      requestAnimationFrame(() => {
        // Force multiple layout calculations for iframe stability
        document.body.offsetHeight;
        document.documentElement.offsetHeight;
        
        // Additional frame wait for iframe context
        requestAnimationFrame(() => {
          // Now trigger visible state for smooth transition
          setIsVisible(true);
        });
      });
      
      // Set up auto-hide timer
      const fadeInDuration = options?.fadeInDuration || 500;
      const displayDuration = options?.displayDuration || 1000;
      const fadeOutDuration = options?.fadeOutDuration || 500;
      
      timerRef.current = setTimeout(() => {
        setIsVisible(false);
        // Remove from DOM after fade out completes
        setTimeout(() => {
          setOverlayContent(null);
        }, fadeOutDuration);
      }, fadeInDuration + displayDuration);
    }
  }, [overlayContent, isVisible, clearOverlay]);

  return React.createElement(OverlayContext.Provider, {
    value: { showOverlay }
  }, [
    children,
    overlayContent && React.createElement('div', {
      key: 'overlay',
      className: `fixed inset-0 z-[9999] transition-all duration-500 pointer-events-auto ${
        isVisible 
          ? 'opacity-100' 
          : 'opacity-0'
      }`,
      style: {
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        width: '100%',
        height: '100%',
        minWidth: '100vw',
        minHeight: '100vh'
      }
    }, overlayContent)
  ]);
};
