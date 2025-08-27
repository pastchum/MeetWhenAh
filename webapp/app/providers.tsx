"use client";

import { NextUIProvider } from "@nextui-org/react";
import { OverlayProvider } from "@/hooks/useOverlay";

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <NextUIProvider>
      <OverlayProvider>
        {children}
      </OverlayProvider>
    </NextUIProvider>
  );
} 