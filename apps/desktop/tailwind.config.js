/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // JARVIS design system — deep charcoal, navy, one blue/cyan accent
        surface: {
          0: '#0a0b0d',    // deepest background
          1: '#0f1117',    // primary background
          2: '#141720',    // card/panel
          3: '#1a1e2a',    // elevated surface
          4: '#20263a',    // hover state
          border: '#1f2535',
        },
        accent: {
          DEFAULT: '#3b82f6',   // blue-500
          dim: '#1d4ed8',       // blue-700
          bright: '#60a5fa',    // blue-400
          cyan: '#06b6d4',      // for voice/active states
          'cyan-dim': '#0891b2',
        },
        text: {
          primary: '#f1f5f9',   // near-white
          secondary: '#94a3b8', // slate-400
          muted: '#475569',     // slate-600
          dim: '#334155',       // slate-700
        },
        status: {
          success: '#10b981',
          warning: '#f59e0b',
          error: '#ef4444',
          info: '#3b82f6',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Consolas', 'monospace'],
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'breathe': 'breathe 4s ease-in-out infinite',
        'slide-in-right': 'slideInRight 0.3s ease-out',
        'fade-in': 'fadeIn 0.2s ease-out',
        'spin-slow': 'spin 3s linear infinite',
      },
      keyframes: {
        breathe: {
          '0%, 100%': { opacity: '0.4', transform: 'scale(1)' },
          '50%': { opacity: '1', transform: 'scale(1.05)' },
        },
        slideInRight: {
          '0%': { transform: 'translateX(100%)', opacity: '0' },
          '100%': { transform: 'translateX(0)', opacity: '1' },
        },
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
      },
      backdropBlur: {
        xs: '2px',
      },
    },
  },
  plugins: [],
}
