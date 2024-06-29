import React from 'react';
import DragSelect from '../_components/DragSelect';

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24">
      <head>
        <script src="https://telegram.org/js/telegram-web-app.js"></script>
      </head>
      <div>
        <h1>Drag to Select Box Example</h1>
        <DragSelect />
      </div>
    </main>
  );
}
