// Color palette for MeetWhenAh - Dark theme with maroon accents
export const colors = {
  // Background colors
  background: {
    primary: '#000000',      // Pure black background
    secondary: '#0a0a0a',    // Slightly lighter black for cards/sections
    tertiary: '#1a1a1a',     // Even lighter for elevated elements
    overlay: 'rgba(0, 0, 0, 0.8)', // Dark overlay for modals
  },

  // Maroon color palette (primary brand color)
  maroon: {
    50: '#fdf2f2',
    100: '#fce7e7',
    200: '#f9d3d3',
    300: '#f4b3b3',
    400: '#ed8585',
    500: '#e25a5a',    // Primary maroon
    600: '#d13a3a',    // Darker maroon for hover states
    700: '#b02a2a',    // Even darker for active states
    800: '#922525',    // Dark maroon for borders
    900: '#7a2020',    // Darkest maroon
  },

  // Text colors
  text: {
    primary: '#ffffff',      // White text
    secondary: '#e5e5e5',    // Slightly muted white
    tertiary: '#a0a0a0',     // Muted gray text
    disabled: '#666666',     // Disabled text
    inverse: '#000000',      // Black text on light backgrounds
  },

  // Border colors
  border: {
    primary: '#333333',      // Dark gray borders
    secondary: '#444444',    // Lighter borders
    accent: '#8b2a2a',       // Maroon borders
    focus: '#d13a3a',        // Maroon focus borders
  },

  // Status colors (avoiding pure red)
  status: {
    success: '#22c55e',      // Green for success
    warning: '#f59e0b',      // Amber for warnings (not red)
    error: '#ef4444',        // Red for errors (reserved for critical issues)
    info: '#3b82f6',         // Blue for info
  },

  // Interactive states
  interactive: {
    hover: '#d13a3a',        // Maroon hover
    active: '#b02a2a',       // Darker maroon for active
    selected: '#8b2a2a',     // Maroon for selected items
    disabled: '#444444',     // Gray for disabled
  },

  // Selection colors (for drag selector)
  selection: {
    primary: 'rgba(210, 58, 58, 0.2)',    // Maroon with transparency
    border: 'rgba(210, 58, 58, 0.4)',     // Maroon border
    hover: 'rgba(210, 58, 58, 0.3)',      // Maroon hover
    active: 'rgba(176, 42, 42, 0.4)',     // Darker maroon active
  },

  // Calendar specific colors
  calendar: {
    header: '#1a1a1a',       // Calendar header background
    timeSlot: '#0a0a0a',     // Time slot background
    selectedSlot: 'rgba(210, 58, 58, 0.3)', // Selected time slot
    hoverSlot: 'rgba(210, 58, 58, 0.1)',   // Hover time slot
    border: '#333333',       // Calendar borders
  },

  // Button colors
  button: {
    primary: {
      background: '#d13a3a',
      text: '#ffffff',
      hover: '#b02a2a',
      active: '#8b2a2a',
      disabled: '#444444',
    },
    secondary: {
      background: 'transparent',
      text: '#ffffff',
      border: '#d13a3a',
      hover: 'rgba(210, 58, 58, 0.1)',
      active: 'rgba(210, 58, 58, 0.2)',
    },
    danger: {
      background: '#ef4444',  // Red for cancel/delete
      text: '#ffffff',
      hover: '#dc2626',
      active: '#b91c1c',
    },
  },
} as const;

// CSS custom properties for easy use in CSS
export const cssVariables = {
  '--color-background-primary': colors.background.primary,
  '--color-background-secondary': colors.background.secondary,
  '--color-background-tertiary': colors.background.tertiary,
  '--color-maroon-primary': colors.maroon[500],
  '--color-maroon-hover': colors.maroon[600],
  '--color-maroon-active': colors.maroon[700],
  '--color-text-primary': colors.text.primary,
  '--color-text-secondary': colors.text.secondary,
  '--color-text-tertiary': colors.text.tertiary,
  '--color-border-primary': colors.border.primary,
  '--color-border-accent': colors.border.accent,
  '--color-selection-primary': colors.selection.primary,
  '--color-selection-border': colors.selection.border,
  '--color-status-success': colors.status.success,
  '--color-status-warning': colors.status.warning,
  '--color-status-error': colors.status.error,
} as const;

// Utility functions
export const colorUtils = {
  // Get maroon color with opacity
  maroonWithOpacity: (opacity: number) => `rgba(210, 58, 58, ${opacity})`,
  
  // Get background color with opacity
  backgroundWithOpacity: (opacity: number) => `rgba(0, 0, 0, ${opacity})`,
  
  // Get text color with opacity
  textWithOpacity: (opacity: number) => `rgba(255, 255, 255, ${opacity})`,
  
  // Check if color is light or dark
  isLight: (color: string) => {
    // Simple heuristic - if it contains 'fff' or high RGB values, it's light
    return color.toLowerCase().includes('fff') || 
           color.toLowerCase().includes('255') ||
           color.toLowerCase().includes('white');
  },
  
  // Get contrasting text color
  getContrastText: (backgroundColor: string) => {
    return colorUtils.isLight(backgroundColor) ? colors.text.inverse : colors.text.primary;
  },
};

// Tailwind CSS classes for common color combinations
export const colorClasses = {
  // Background classes
  bgPrimary: 'bg-black',
  bgSecondary: 'bg-[#0a0a0a]',
  bgTertiary: 'bg-[#1a1a1a]',
  
  // Maroon classes
  bgMaroon: 'bg-[#d13a3a]',
  bgMaroonHover: 'hover:bg-[#b02a2a]',
  bgMaroonActive: 'active:bg-[#8b2a2a]',
  textMaroon: 'text-[#d13a3a]',
  borderMaroon: 'border-[#d13a3a]',
  
  // Text classes
  textPrimary: 'text-white',
  textSecondary: 'text-[#e5e5e5]',
  textTertiary: 'text-[#a0a0a0]',
  
  // Border classes
  borderPrimary: 'border-[#333333]',
  borderSecondary: 'border-[#444444]',
  
  // Selection classes
  selectionPrimary: 'bg-[rgba(210,58,58,0.2)]',
  selectionBorder: 'border-[rgba(210,58,58,0.4)]',
  selectionHover: 'hover:bg-[rgba(210,58,58,0.3)]',
  
  // Status classes
  statusSuccess: 'text-[#22c55e]',
  statusWarning: 'text-[#f59e0b]',
  statusError: 'text-[#ef4444]',
  
  // Button classes
  btnPrimary: 'bg-[#d13a3a] text-white hover:bg-[#b02a2a] active:bg-[#8b2a2a]',
  btnSecondary: 'bg-transparent text-white border border-[#d13a3a] hover:bg-[rgba(210,58,58,0.1)]',
  btnDanger: 'bg-[#ef4444] text-white hover:bg-[#dc2626] active:bg-[#b91c1c]',
} as const; 