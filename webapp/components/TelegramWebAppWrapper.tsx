"use client";
import React from 'react';

interface TelegramWebAppWrapperProps {
  children: React.ReactNode;
}

export default function TelegramWebAppWrapper({ children }: TelegramWebAppWrapperProps) {
  // Only show wrapper in development and when explicitly enabled
  const shouldShowWrapper = process.env.NODE_ENV === 'development' && 
                           process.env.NEXT_PUBLIC_ENABLE_TELEGRAM_MOCK !== 'false';
  
  if (!shouldShowWrapper) {
    return <>{children}</>;
  }

  return (
    <div className="telegram-webapp-wrapper">
      {/* Telegram Web App Header */}
      <div className="telegram-header">
        <div className="telegram-header-content">
          <div className="telegram-back-button">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <path d="M15 18L9 12L15 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </div>
          <div className="telegram-title">MeetWhenAh</div>
          <div className="telegram-menu-button">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <circle cx="12" cy="12" r="1" fill="currentColor"/>
              <circle cx="19" cy="12" r="1" fill="currentColor"/>
              <circle cx="5" cy="12" r="1" fill="currentColor"/>
            </svg>
          </div>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="telegram-content">
        {children}
      </div>

      {/* Telegram Web App Footer/Main Button Area */}
      <div className="telegram-footer">
        <div className="telegram-main-button">
          <span>Continue</span>
        </div>
      </div>

      <style jsx>{`
        .telegram-webapp-wrapper {
          width: 100%;
          max-width: 414px; /* iPhone width */
          height: 100vh;
          margin: 0 auto;
          background: #1a1a1a;
          color: #ffffff;
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
          position: relative;
          overflow: hidden;
          border-radius: 12px;
          box-shadow: 0 0 20px rgba(0, 0, 0, 0.3);
        }

        .telegram-header {
          height: 44px;
          background: #1a1a1a;
          border-bottom: 1px solid #2a2a2a;
          position: relative;
          z-index: 10;
        }

        .telegram-header-content {
          display: flex;
          align-items: center;
          justify-content: space-between;
          height: 100%;
          padding: 0 16px;
        }

        .telegram-back-button,
        .telegram-menu-button {
          width: 44px;
          height: 44px;
          display: flex;
          align-items: center;
          justify-content: center;
          color: #2481cc;
          cursor: pointer;
        }

        .telegram-title {
          font-size: 17px;
          font-weight: 600;
          color: #ffffff;
          flex: 1;
          text-align: center;
        }

        .telegram-content {
          flex: 1;
          overflow-y: auto;
          background: #1a1a1a;
          height: calc(100vh - 44px - 60px); /* Subtract header and footer */
          display: flex;
          flex-direction: column;
        }

        .telegram-footer {
          height: 60px;
          background: #1a1a1a;
          border-top: 1px solid #2a2a2a;
          padding: 8px 16px;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .telegram-main-button {
          background: #2481cc;
          color: #ffffff;
          padding: 12px 24px;
          border-radius: 8px;
          font-size: 16px;
          font-weight: 500;
          cursor: pointer;
          transition: background-color 0.2s;
        }

        .telegram-main-button:hover {
          background: #1e6bb8;
        }

        /* Responsive adjustments */
        @media (max-width: 414px) {
          .telegram-webapp-wrapper {
            max-width: 100%;
            border-radius: 0;
          }
        }

        /* Dark theme adjustments */
        .telegram-webapp-wrapper {
          --tg-theme-bg-color: #1a1a1a;
          --tg-theme-text-color: #ffffff;
          --tg-theme-hint-color: #999999;
          --tg-theme-link-color: #2481cc;
          --tg-theme-button-color: #2481cc;
          --tg-theme-button-text-color: #ffffff;
          --tg-theme-secondary-bg-color: #2a2a2a;
        }
      `}</style>
    </div>
  );
} 