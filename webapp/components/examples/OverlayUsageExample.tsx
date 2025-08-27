import React from 'react';
import { useOverlay } from '@/hooks/useOverlay';

// Example component showing how other pages can use the global overlay system
export default function OverlayUsageExample() {
  const { showOverlay } = useOverlay();

  const showSuccessOverlay = () => {
    showOverlay((
      <div className="fixed inset-0 bg-black bg-opacity-70 flex items-center justify-center z-[9999] transition-all duration-500">
        <div className="bg-white rounded-lg p-6 max-w-sm mx-4 text-center minecraft-font shadow-[4px_4px_0px_0px_rgba(0,0,0,0.8)] transition-all duration-500">
          <div className="text-2xl mb-2">✅</div>
          <h3 className="text-lg font-bold text-gray-800 mb-2">Event Confirmed!</h3>
          <p className="text-gray-600 text-sm mb-4">
            Your availability has been saved successfully.
          </p>
        </div>
      </div>
    ), {
      fadeInDuration: 500,
      displayDuration: 3000,
      fadeOutDuration: 500
    });
  };

  const showErrorOverlay = () => {
    showOverlay((
      <div className="fixed inset-0 bg-black bg-opacity-70 flex items-center justify-center z-[9999] transition-all duration-500">
        <div className="bg-red-100 border border-red-400 rounded-lg p-6 max-w-sm mx-4 text-center minecraft-font shadow-[4px_4px_0px_0px_rgba(0,0,0,0.8)] transition-all duration-500">
          <div className="text-2xl mb-2">⚠️</div>
          <h3 className="text-lg font-bold text-red-800 mb-2">Oops!</h3>
          <p className="text-red-600 text-sm mb-4">
            Something went wrong. Please try again.
          </p>
        </div>
      </div>
    ), {
      fadeInDuration: 300,
      displayDuration: 4000,
      fadeOutDuration: 300
    });
  };

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-gray-800">Overlay Examples</h3>
      <div className="flex space-x-2">
        <button
          onClick={showSuccessOverlay}
          className="bg-green-500 hover:bg-green-600 text-white px-3 py-1 rounded text-sm transition-all duration-150 minecraft-font shadow-[2px_2px_0px_0px_rgba(0,0,0,0.6)] hover:shadow-[3px_3px_0px_0px_rgba(0,0,0,0.7)]"
        >
          Show Success
        </button>
        <button
          onClick={showErrorOverlay}
          className="bg-red-500 hover:bg-red-600 text-white px-3 py-1 rounded text-sm transition-all duration-150 minecraft-font shadow-[2px_2px_0px_0px_rgba(0,0,0,0.6)] hover:shadow-[3px_3px_0px_rgba(0,0,0,0.7)]"
        >
          Show Error
        </button>
      </div>
    </div>
  );
}
