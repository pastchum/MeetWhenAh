import { ForwardIcon } from '@heroicons/react/24/solid';
import { Button } from '@nextui-org/react';

export default function SubmitButton({onClick, disabled}) {
  return (
    <>
      <Button
        type="button"
        disabled={disabled}
        onClick={() => onClick()}
        variant="solid"
        color="primary"
        size="sm"
        className="bg-[#8c2e2e] hover:bg-[#722525]"
        data-testid="submitbutton"
        endContent={<ForwardIcon className="h-3 w-3" aria-hidden="true" />}
      >
        Submit
      </Button>
    </>
  )
}