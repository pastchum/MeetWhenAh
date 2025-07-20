"use client";
import { useEffect } from 'react';

// Mock Telegram Web App environment for development
export function useTelegramMock() {
  useEffect(() => {
    // Only mock in development and when explicitly enabled
    const shouldMock = process.env.NODE_ENV === 'development'
    
    if (shouldMock && typeof window !== 'undefined' && !window.Telegram?.WebApp) {
      // Create mock Telegram Web App object
      const mockWebApp = {
        initData: '',
        initDataUnsafe: {
          user: null,
          chat: null,
          chat_type: null,
          chat_instance: null,
          start_param: null,
          can_send_after: null,
          auth_date: null,
          hash: null,
        },
        version: '8.0',
        platform: 'ios',
        colorScheme: 'dark',
        themeParams: {
          bg_color: '#1a1a1a',
          text_color: '#ffffff',
          hint_color: '#999999',
          link_color: '#2481cc',
          button_color: '#2481cc',
          button_text_color: '#ffffff',
          secondary_bg_color: '#2a2a2a',
        },
        isExpanded: false,
        viewportHeight: 600,
        viewportStableHeight: 600,
        headerColor: '#1a1a1a',
        backgroundColor: '#1a1a1a',
        isClosingConfirmationEnabled: false,
        backButton: {
          isVisible: false,
          onClick: (callback: () => void) => {
            console.log('[TMA-mock] Back button clicked');
            callback();
          },
          show: () => {
            console.log('[TMA-mock] Back button shown');
          },
          hide: () => {
            console.log('[TMA-mock] Back button hidden');
          },
        },
        mainButton: {
          text: '',
          color: '#2481cc',
          textColor: '#ffffff',
          isVisible: false,
          isProgressVisible: false,
          isActive: true,
          onClick: (callback: () => void) => {
            console.log('[TMA-mock] Main button clicked');
            callback();
          },
          show: () => {
            console.log('[TMA-mock] Main button shown');
          },
          hide: () => {
            console.log('[TMA-mock] Main button hidden');
          },
          enable: () => {
            console.log('[TMA-mock] Main button enabled');
          },
          disable: () => {
            console.log('[TMA-mock] Main button disabled');
          },
          showProgress: () => {
            console.log('[TMA-mock] Main button progress shown');
          },
          hideProgress: () => {
            console.log('[TMA-mock] Main button progress hidden');
          },
          setText: (text: string) => {
            console.log('[TMA-mock] Main button text set to:', text);
          },
          setParams: (params: any) => {
            console.log('[TMA-mock] Main button params set:', params);
          },
        },
        HapticFeedback: {
          impactOccurred: (style: 'light' | 'medium' | 'heavy' | 'rigid' | 'soft') => {
            console.log('[TMA-mock] Haptic feedback:', style);
          },
          notificationOccurred: (type: 'error' | 'success' | 'warning') => {
            console.log('[TMA-mock] Notification haptic:', type);
          },
          selectionChanged: () => {
            console.log('[TMA-mock] Selection haptic');
          },
        },
        ready: () => {
          console.log('[TMA-mock] WebApp ready');
        },
        expand: () => {
          console.log('[TMA-mock] WebApp expanded');
        },
        close: () => {
          console.log('[TMA-mock] WebApp close requested');
        },
        sendData: (data: string) => {
          console.log('[TMA-mock] Data sent:', data);
        },
        switchInlineQuery: (query: string, choose_chat_types?: string[]) => {
          console.log('[TMA-mock] Switch inline query:', query, choose_chat_types);
        },
        openLink: (url: string, options?: { try_instant_view?: boolean }) => {
          console.log('[TMA-mock] Open link:', url, options);
          window.open(url, '_blank');
        },
        openTelegramLink: (url: string) => {
          console.log('[TMA-mock] Open Telegram link:', url);
        },
        openInvoice: (url: string, callback?: (status: string) => void) => {
          console.log('[TMA-mock] Open invoice:', url);
          if (callback) callback('paid');
        },
        showPopup: (params: { title?: string; message: string; buttons?: any[] }, callback?: (buttonId: string) => void) => {
          console.log('[TMA-mock] Show popup:', params);
          if (callback) callback('ok');
        },
        showAlert: (message: string, callback?: () => void) => {
          console.log('[TMA-mock] Show alert:', message);
          alert(message);
          if (callback) callback();
        },
        showConfirm: (message: string, callback?: (confirmed: boolean) => void) => {
          console.log('[TMA-mock] Show confirm:', message);
          const confirmed = confirm(message);
          if (callback) callback(confirmed);
        },
        showScanQrPopup: (params: { text?: string }, callback?: (data: string) => void) => {
          console.log('[TMA-mock] Show QR scanner:', params);
          if (callback) callback('mock-qr-data');
        },
        closeScanQrPopup: () => {
          console.log('[TMA-mock] Close QR scanner');
        },
        readTextFromClipboard: (callback?: (data: string) => void) => {
          console.log('[TMA-mock] Read clipboard');
          if (callback) callback('mock-clipboard-data');
        },
        requestWriteAccess: (callback?: (access: boolean) => void) => {
          console.log('[TMA-mock] Request write access');
          if (callback) callback(true);
        },
        requestContact: (callback?: (contact: any) => void) => {
          console.log('[TMA-mock] Request contact');
          if (callback) callback({ phone_number: '+1234567890', first_name: 'Mock', last_name: 'User' });
        },
        invokeCustomMethod: (method: string, params?: any) => {
          console.log('[TMA-mock] Custom method:', method, params);
        },
        offEvent: (eventType: string, eventHandler: Function) => {
          console.log('[TMA-mock] Event handler removed:', eventType);
        },
        onEvent: (eventType: string, eventHandler: Function) => {
          console.log('[TMA-mock] Event handler added:', eventType);
        },
        setHeaderColor: (color: string) => {
          console.log('[TMA-mock] Header color set:', color);
        },
        setBackgroundColor: (color: string) => {
          console.log('[TMA-mock] Background color set:', color);
        },
        enableClosingConfirmation: () => {
          console.log('[TMA-mock] Closing confirmation enabled');
        },
        disableClosingConfirmation: () => {
          console.log('[TMA-mock] Closing confirmation disabled');
        },
        isVersionAtLeast: (version: string) => {
          console.log('[TMA-mock] Version check:', version);
          return true;
        },
      };

      // Attach to window
      (window as any).Telegram = {
        WebApp: mockWebApp,
      };

      console.log('[TMA-mock] Telegram Web App environment mocked for development');
    }
  }, []);
} 