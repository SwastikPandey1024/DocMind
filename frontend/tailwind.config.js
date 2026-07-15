/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#eff6ff',
          500: '#2563eb',
          600: '#2563eb',
          700: '#1d4ed8',
        },
        accent: '#14b8a6',
      },
      boxShadow: {
        soft: '0 20px 45px -20px rgba(15, 23, 42, 0.35)',
      },
    },
  },
  plugins: [],
};
