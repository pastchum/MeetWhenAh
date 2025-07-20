"use client";
import React from 'react';
import { useTelegramMock } from "@/hooks/useTelegramMock";
import TelegramWebAppWrapper from "@/components/TelegramWebAppWrapper";

interface TelegramProviderProps {
  children: React.ReactNode;
}

export default function TelegramProvider({ children }: TelegramProviderProps) {
  useTelegramMock();
  
  return (
    <TelegramWebAppWrapper>
      {children}
    </TelegramWebAppWrapper>
  );
} 