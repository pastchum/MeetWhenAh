import React from 'react'
import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import CreateEvent from "./pages/CreateEvent";
import SetAvailability from "./pages/SetAvailability";
import '@/index.css'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="createEvent" element={<CreateEvent />} />
        <Route path="setAvailability" element={<SetAvailability />} />
      </Routes>
    </BrowserRouter>
  );
}

const root = ReactDOM.createRoot(document.getElementById("root") as HTMLElement);
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);