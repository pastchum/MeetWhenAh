import {nextui} from '@nextui-org/theme';
import type { Config } from "tailwindcss";


const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./node_modules/@nextui-org/theme/dist/components/(date-picker|button|ripple|spinner|calendar|date-input|popover).js"
  ],
  darkMode : ['class', "class"],
  theme: {
  	extend: {
  		fontFamily: {
  			'minecraft': ['Minecraft', 'monospace'],
  			'ibm-mono': ['IBM Plex Mono', 'monospace'],
  			'body': ['IBM Plex Mono', 'monospace'],
  			'heading': ['Minecraft', 'monospace'],
  			'instruction': ['IBM Plex Mono', 'monospace'],
  			'ui': ['IBM Plex Mono', 'monospace'],
  			'caption': ['IBM Plex Mono', 'monospace'],
  		},
  		colors: {
  			selection: {
  				primary: 'rgba(200, 80, 80, 0.8)',
  				border: 'rgba(200, 80, 80, 0.9)',
  				hover: 'rgba(220, 100, 100, 0.9)',
  				active: 'rgba(180, 70, 70, 0.9)'
  			}
  		},
  		boxShadow: {
  			'custom-inset': 'inset 0 0 0 2px rgba(210, 58, 58, 0.5)',
  			'maroon-glow': '0 0 20px rgba(210, 58, 58, 0.3)'
  		},
  		gridTemplateRows: {
  			'49': 'repeat(49, minmax(0, 1fr))'
  		},
  		backgroundImage: {
  			'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
  			'gradient-conic': 'conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))',
  			'maroon-gradient': 'linear-gradient(135deg, #d13a3a 0%, #b02a2a 100%)'
  		},

  	}
  },
  variants: {
    extend: {
      mixBlendMode: ['responsive', 'hover', 'focus'],
    },
  },
  plugins: [
    nextui({
      themes: {
        dark: {
          colors: {
            primary: {
              50: '#fdf2f2',
              100: '#fce7e7',
              200: '#f9d3d3',
              300: '#f4b3b3',
              400: '#ed8585',
              500: '#c44545',
              600: '#a83838',
              700: '#8c2e2e',
              800: '#722525',
              900: '#5a1e1e',
              DEFAULT: '#8c2e2e',
              foreground: '#ffffff',
            },
            default: {
              50: '#f8f9fa',
              100: '#f1f3f4',
              200: '#e8eaed',
              300: '#dadce0',
              400: '#bdc1c6',
              500: '#9aa0a6',
              600: '#80868b',
              700: '#5f6368',
              800: '#3c4043',
              900: '#202124',
              DEFAULT: '#3c4043',
              foreground: '#ffffff',
            },
            background: '#000000',
            foreground: '#ffffff',
            focus: '#8c2e2e',
          },
        },
      },
    }),
    require("tailwindcss-animate")
  ],
};
export default config;
