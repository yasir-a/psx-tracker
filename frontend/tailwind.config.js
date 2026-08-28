/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        psx: {
          green: '#00875A',
          red: '#DE350B',
          dark: '#091E42',
          muted: '#6B778C',
          light: '#F4F5F7',
          border: '#DFE1E6',
        }
      }
    },
  },
  plugins: [],
}