/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: "#18181B",
        secondary: "#3F3F46",
        cta: "#2563EB",
        accent: "#2563EB",
        background: "#FAFAFA",
        lifelogText: "#09090B",
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
      boxShadow: {
        'lifelog-sm': '0 1px 2px rgba(0,0,0,0.05)',
        'lifelog-md': '0 4px 6px rgba(0,0,0,0.1)',
        'lifelog-lg': '0 10px 15px rgba(0,0,0,0.1)',
        'lifelog-xl': '0 20px 25px rgba(0,0,0,0.15)',
      }
    },
  },
  plugins: [],
}
