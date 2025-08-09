import { ForwardIcon } from '@heroicons/react/24/solid';
import { Button } from '@nextui-org/react';

export default function RemoveNightButton({ onClick }) {
  
  return (
    <>
      <Button
        type="button"
        onClick={() => onClick()}
        variant="bordered"
        color="primary"
        size="sm"
        className="border-[#8c2e2e] text-[#8c2e2e] hover:bg-[#8c2e2e] hover:text-white"
      >
        Toggle full day
      </Button>
    </>
  )
}