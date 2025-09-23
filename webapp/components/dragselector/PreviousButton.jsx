import { BackwardIcon } from '@heroicons/react/24/solid'
import { Button } from '@nextui-org/react';

export default function PreviousButton({onClick, disabled}) {
  return (
    <>
      <Button
        type="button"
        onClick={onClick}
        disabled={disabled}
        variant="solid"
        color="primary"
        size="sm"
        className="bg-[#8c2e2e] hover:bg-[#722525] font-ui"
        data-testid="previousbutton2"
        startContent={<BackwardIcon className="h-3 w-3" aria-hidden="true" />}
      >
        Previous
      </Button>
    </>
  )
}