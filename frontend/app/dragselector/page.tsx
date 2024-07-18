'use client'

import React, { useRef, useContext, createContext, forwardRef, ReactNode, useState } from 'react';
import DragSelector from '@/components/dragselector/DragSelector'




export default function Home() {  

  

  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24 w-screen">
      <head>
        <script src="https://telegram.org/js/telegram-web-app.js"></script>
      </head>
      <DragSelector />
    </main>
  );
}
