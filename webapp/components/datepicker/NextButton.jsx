import { useState } from 'react';

export default function NextButton({onClick, newData , disabled}) {
  
  return (
    <>
      <button
        type="button"
        disabled={disabled}
        onClick={() => onClick(newData)}
        className="inline-flex items-center justify-center gap-x-2 rounded-md bg-[#8c2e2e] px-4 py-3 text-sm font-semibold text-white shadow-lg shadow-[#8c2e2e]/20 hover:bg-[#722525] hover:shadow-md hover:shadow-[#c44545]/30 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#8c2e2e] disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-150 minecraft-font border-2 border-[#8c2e2e]"
        data-testid='nextbutton'
      >
        <span className="minecraft-font">Next</span>
        <span className="text-white minecraft-font text-sm leading-none transform -translate-y-0.5">▶</span>
      </button>
    </>
  )
}