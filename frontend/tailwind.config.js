/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-conic': 'conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))',
      },
      boxShadow: {
        'custom-light': '0 10px 40px rgba(0, 0, 0, 0.1)',
        'custom-dark': '0 10px 50px rgba(0, 0, 0, 0.3)',
      },
      backdropBlur: {
        'xs': '2px',
        'sm': '4px',
      },
      animation: {
        'background-shine': 'background-shine 2s linear infinite',
        'pulse-slow': 'pulse 3s infinite',
      },
      keyframes: {
        'background-shine': {
          '0%': { backgroundPosition: '0 0' },
          '100%': { backgroundPosition: '-200% 0' },
        },
        'mouse-track': {
          '0%': { transform: 'translate(-50%, -50%) scale(0.8)' },
          '50%': { transform: 'translate(-50%, -50%) scale(1)' },
          '100%': { transform: 'translate(-50%, -50%) scale(0.8)' },
        }
      }
    },
  },
  plugins: [],
}
