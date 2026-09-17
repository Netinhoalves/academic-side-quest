/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'color-blue-light': '#3853A4',
        'color-blue': '#172B68',
        'color-blue-dark': '#112131',
        'color-red': '#C32722',
        'color-orange': '#E9A344',
        'color-orange-bright': '#F29334',
        'color-yellow': '#FFB44E',
        'color-green': '#32B788',
        'color-creme': '#FFF7EE',
      },
      fontFamily: {
        'jaro': ['"Jaro"', 'sans-serif'],
      }
    },
  },
  plugins: [],
}