import {nextui} from '@nextui-org/theme';
import type { Config } from "tailwindcss";


const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./node_modules/@nextui-org/theme/dist/components/(date-picker|button|ripple|spinner|calendar|date-input|popover).js"
  ],
  darkMode : 'class',
  theme: {
    extend: {
      colors: {
        'custom-blue': 'hsl(206deg 100% 50% / 5%)',
      },
      boxShadow: {
        'custom-inset': 'inset 0 0 0 2px hsl(206deg 100% 50% / 50%)',
      },
      gridTemplateRows: {        
        // Simple 48 column grid        
        '49': 'repeat(49, minmax(0, 1fr))',     
      },    
      backgroundImage: {
        "gradient-radial": "radial-gradient(var(--tw-gradient-stops))",
        "gradient-conic":
          "conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))",
      },
    },
  },
  variants: {
    extend: {
      mixBlendMode: ['responsive', 'hover', 'focus'],
    },
  },
  plugins: [nextui()],
};
export default config;
