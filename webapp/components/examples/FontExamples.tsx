"use client";

import React from 'react';

export default function FontExamples() {
  return (
    <div className="p-8 bg-black text-white space-y-8">
      <h1 className="text-4xl font-title mb-8">Font System Examples</h1>
      
      {/* Minecraft Font Examples */}
      <section className="space-y-4">
        <h2 className="text-2xl font-heading text-red-500">Minecraft Font (Titles & Headers)</h2>
        <div className="space-y-2">
          <h3 className="text-xl font-heading">Main Page Title</h3>
          <h4 className="text-lg font-heading">Section Header</h4>
          <p className="text-sm font-heading text-gray-400">Game-like UI elements</p>
        </div>
      </section>

      {/* IBM Plex Mono Font Examples */}
      <section className="space-y-4">
        <h2 className="text-2xl font-heading text-blue-500">IBM Plex Mono Font (Body & UI)</h2>
        
        <div className="space-y-2">
          <h3 className="text-lg font-ui text-green-400">UI Elements</h3>
          <button className="px-4 py-2 bg-red-600 text-white font-ui rounded">
            Button Text
          </button>
          <label className="block text-sm font-ui text-yellow-400">
            Form Label
          </label>
        </div>

        <div className="space-y-2">
          <h3 className="text-lg font-body text-green-400">Body Text</h3>
          <p className="font-body">
            This is regular body text using IBM Plex Mono. It's perfect for instructions, 
            descriptions, and general content. The monospace font gives it a command-line 
            aesthetic while maintaining excellent readability.
          </p>
        </div>

        <div className="space-y-2">
          <h3 className="text-lg font-instruction text-green-400">Instructions</h3>
          <p className="font-instruction">
            Step 1: Select your available time slots<br/>
            Step 2: Review your selections<br/>
            Step 3: Submit your availability
          </p>
        </div>

        <div className="space-y-2">
          <h3 className="text-lg font-caption text-green-400">Captions & Subtle Text</h3>
          <p className="font-caption text-gray-400">
            Last updated: 2024-01-15 14:30:00
          </p>
          <p className="font-caption text-gray-500">
            Optional information or secondary details
          </p>
        </div>

        <div className="space-y-2">
          <h3 className="text-lg font-code text-green-400">Code-like Text</h3>
          <div className="bg-gray-800 p-3 rounded font-code text-sm">
            <code>
              {`const event = {
  name: "Team Meeting",
  date: "2024-01-20",
  time: "14:00"
};`}
            </code>
          </div>
        </div>
      </section>

      {/* Font Weight Examples */}
      <section className="space-y-4">
        <h2 className="text-2xl font-heading text-purple-500">Font Weight Examples</h2>
        <div className="space-y-2 font-body">
          <p className="font-thin">Thin (100): Very light text</p>
          <p className="font-extralight">Extra Light (200): Light text</p>
          <p className="font-light">Light (300): Light text</p>
          <p className="font-normal">Regular (400): Normal text</p>
          <p className="font-medium">Medium (500): Medium text</p>
          <p className="font-semibold">Semi Bold (600): Semi bold text</p>
          <p className="font-bold">Bold (700): Bold text</p>
        </div>
      </section>

      {/* Usage Guidelines */}
      <section className="space-y-4">
        <h2 className="text-2xl font-heading text-orange-500">Usage Guidelines</h2>
        <div className="space-y-3 font-body text-sm">
          <div className="p-4 bg-gray-900 rounded">
            <h4 className="font-ui text-yellow-400 mb-2">When to use Minecraft font:</h4>
            <ul className="list-disc list-inside space-y-1 font-body">
              <li>Main page titles and headers</li>
              <li>Game-like UI elements</li>
              <li>Brand elements that need retro gaming feel</li>
            </ul>
          </div>
          
          <div className="p-4 bg-gray-900 rounded">
            <h4 className="font-ui text-yellow-400 mb-2">When to use IBM Plex Mono:</h4>
            <ul className="list-disc list-inside space-y-1 font-body">
              <li>All body text and content</li>
              <li>Form labels and UI elements</li>
              <li>Instructions and descriptions</li>
              <li>Code-like or technical content</li>
              <li>Captions and secondary information</li>
            </ul>
          </div>
        </div>
      </section>
    </div>
  );
}
