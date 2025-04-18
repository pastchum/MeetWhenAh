import { ForwardIcon } from '@heroicons/react/24/solid';
import { useState } from 'react';
export default function NextButton({onClick, newData , disabled}) {
  
  return (
    <>
      <button
        type="button"
        disabled={disabled}
        onClick={() => onClick(newData)}
        className="inline-flex items-center gap-x-2 rounded-md bg-indigo-600 px-3.5 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
        data-testid='nextbutton'
      >
        Next
        <ForwardIcon className="-mr-0.5 h-5 w-5" aria-hidden="true" />
      </button>
    </>
  )
}