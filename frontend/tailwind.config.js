/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js}'],
  theme: {
    extend: {
      colors: {
        primary: '#005daa',
        'on-primary': '#ffffff',
        'primary-container': '#0075d5',
        background: '#fcf9f8',
        'on-background': '#1b1b1c',
        surface: '#fcf9f8',
        'surface-container-low': '#f6f3f2',
        'surface-container-high': '#eae7e7',
        'outline-variant': '#c0c7d6',
        'on-surface': '#1b1b1c',
        'on-surface-variant': '#404753',
        secondary: '#006d33',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'PingFang SC', 'Microsoft YaHei', 'sans-serif'],
      },
      boxShadow: {
        card: '0px 4px 12px rgba(0, 0, 0, 0.05)',
        elevated: '0px 8px 24px rgba(0, 0, 0, 0.08)',
      },
    },
  },
  plugins: [],
}
