import { ForwardIcon } from '@heroicons/react/24/solid';
import { useState } from 'react';
export default function RemoveNightButton({ onClick }) {
  
  return (
    <>
      <button
        type="button"
        onClick={() => onClick()}
        className="inline-flex items-center gap-x-2 rounded-md bg-indigo-600 px-3.5 py-2.5 text-xs font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
      >
        Toggle full day
      </button>
    </>
  )
}