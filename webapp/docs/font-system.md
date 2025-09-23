# Font System Documentation

## Overview

This project uses a dual-font system optimized for both gaming aesthetics and command-line/8-bit style:

- **Minecraft font**: For titles, headers, and game-like elements
- **IBM Plex Mono font**: For body text, instructions, UI elements, and command-line style text

## Font Families

### 1. Minecraft Font (`font-minecraft` / `font-heading` / `font-title`)
- **Usage**: Main titles, headers, game-like elements
- **Characteristics**: Pixelated, retro gaming aesthetic
- **Best for**: Page titles, section headers, game UI elements
- **Example**: `className="font-title text-4xl"`

### 2. IBM Plex Mono Font (`font-body` / `font-instruction` / `font-ui` / `font-caption`)
- **Usage**: Body text, instructions, UI elements, command-line style text
- **Characteristics**: Monospace, command-line aesthetic, highly readable
- **Best for**: Instructions, descriptions, form labels, UI text, code-like elements
- **Example**: `className="font-instruction text-sm"`

## Tailwind Classes

### Font Family Classes
```css
font-minecraft    /* Minecraft font */
font-ibm-mono     /* IBM Plex Mono font */
font-body         /* IBM Plex Mono font (default) */
font-heading      /* Minecraft font (alias) */
font-instruction  /* IBM Plex Mono font with optimized settings */
font-title        /* Minecraft font with letter spacing */
font-ui           /* IBM Plex Mono font for UI elements */
font-caption      /* IBM Plex Mono font for captions */
font-code         /* IBM Plex Mono font for code-like text */
```

### Usage Examples

#### Main Page Title
```jsx
<h1 className="font-title text-6xl text-center mb-8">
  MeetWhenAh
</h1>
```

#### Section Headers
```jsx
<h2 className="font-heading text-3xl mb-4">
  Select Your Availability
</h2>
```

#### Instructions
```jsx
<p className="font-instruction text-base text-gray-300 mb-4">
  Click and drag to select your available time slots. 
  The selected times will be highlighted in red.
</p>
```

#### Body Text
```jsx
<div className="font-body text-sm text-gray-400">
  This is regular body text that should be easy to read.
</div>
```

## Typography Scale

### Headings (Minecraft Font)
- `text-6xl` - Main page title
- `text-4xl` - Section headers
- `text-2xl` - Subsection headers
- `text-xl` - Card titles

### Body Text (Inter Font)
- `text-lg` - Large body text
- `text-base` - Regular body text
- `text-sm` - Small text, captions
- `text-xs` - Very small text, labels

## Best Practices

### 1. Use Minecraft for:
- Page titles and main headings
- Game-like UI elements
- Navigation headers
- Brand elements

### 2. Use Inter for:
- Instructions and help text
- Form labels and descriptions
- Body content
- Error messages
- Any text that needs to be easily readable

### 3. Font Weight Guidelines
- **Minecraft**: Always use `font-normal` (no weight variations)
- **Inter**: Use `font-light` (300), `font-normal` (400), `font-medium` (500), `font-semibold` (600)

### 4. Line Height
- **Minecraft**: Use default line height
- **Inter**: Use `leading-relaxed` (1.625) or `leading-loose` (2) for better readability

## Implementation Examples

### Component Structure
```jsx
export function PageHeader({ title, subtitle }) {
  return (
    <div className="text-center mb-8">
      <h1 className="font-title text-6xl mb-4">
        {title}
      </h1>
      {subtitle && (
        <p className="font-instruction text-lg text-gray-300">
          {subtitle}
        </p>
      )}
    </div>
  );
}
```

### Form Component
```jsx
export function FormField({ label, children, helpText }) {
  return (
    <div className="mb-6">
      <label className="font-body text-sm font-medium text-white mb-2 block">
        {label}
      </label>
      {children}
      {helpText && (
        <p className="font-instruction text-xs text-gray-400 mt-1">
          {helpText}
        </p>
      )}
    </div>
  );
}
```

## Migration Guide

### From Old Font System
1. Replace `font-minecraft` with `font-title` for main titles
2. Replace `font-minecraft` with `font-heading` for section headers
3. Add `font-instruction` to instruction text
4. Use `font-body` for general UI text

### Before
```jsx
<h1 className="font-minecraft text-4xl">Title</h1>
<p className="text-sm">Instructions here</p>
```

### After
```jsx
<h1 className="font-title text-4xl">Title</h1>
<p className="font-instruction text-sm">Instructions here</p>
```

## Performance Notes

- Inter font is loaded from Google Fonts with `display=swap` for optimal loading
- Minecraft font is loaded locally for consistent availability
- Both fonts use `font-display: swap` to prevent layout shift
