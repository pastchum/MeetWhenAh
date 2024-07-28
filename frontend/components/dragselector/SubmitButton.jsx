import { ForwardIcon } from '@heroicons/react/24/solid';
export default function SubmitButton({onClick, disabled}) {
  return (
    <>
      <button
        type="button"
        disabled={disabled}
        onClick={
          () => onClick() 
        }
        className="inline-flex items-center gap-x-2 rounded-md bg-indigo-600 px-3.5 py-2.5 text-xs font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
      >
        Submit
        <ForwardIcon className="-mr-0.5 h-3 w-3" aria-hidden="true" />
      </button>
    </>
  )
}