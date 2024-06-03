import React from 'react'
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog"
import { Button } from '@/components/ui/button'

type ChildComponentProps = {
  handleEventMessage: () => void;
  handleEdit: () => void;
  handleExit: () => void
};
const EventMessage: React.FC<ChildComponentProps>  = ({handleEventMessage, handleEdit, handleExit }) => {

  const formatDate = (date: Date | null): string | null => {
    return date ? date.toLocaleDateString() : null; // Or use toLocaleDateString(), etc.
  };
  // const start = formatDate(startDate);
  // const end = formatDate(endDate);
  return (
    <div className='h-screen flex flex-col text-start justify-center items-center mx-20 p-4 m-auto'>
        <Alert>
        <AlertTitle> <h2 className="scroll-m-20 pb-2 text-3xl font-semibold tracking-tight first:mt-0">
          Jensen Turns One
    </h2></AlertTitle>
        <AlertDescription>
        <h4 className="scroll-m-20 text-xl pb-2 border-b font-semibold tracking-tight">
      Date Range: 25th January - 26th January
    </h4>
    <p className="leading-7 [&:not(:first-child)]:mt-6"> This is a template, here you would see your description for the event!   </p>
        </AlertDescription>
    </Alert>
  
    <div className = "mt-5 flex justify-between w-full">< Button onClick = {handleEdit} variant = "secondary"> edit date range
    </Button>
    <AlertDialog>
  <AlertDialogTrigger onClick = {handleEventMessage} className = " rounded-md justify-center text-sm border border-input bg-background hover:bg-accent hover:text-accent-foreground h-10 px-4 py-2 ">
    finalise dates</AlertDialogTrigger>
  <AlertDialogContent>
    <AlertDialogHeader>
      <AlertDialogTitle>Your event proposal has been created!</AlertDialogTitle>
      <AlertDialogDescription>
        Share to your group!
      </AlertDialogDescription>
    </AlertDialogHeader>
    <AlertDialogFooter>
      <AlertDialogCancel onClick = {handleExit}>exit</AlertDialogCancel>
    </AlertDialogFooter>
  </AlertDialogContent>
</AlertDialog></div>
</div>
  )
}

export default EventMessage