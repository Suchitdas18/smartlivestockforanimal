/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // Primary colors - Forest/Leaf Green
        primary: {
          50: '#E8F5E9',
          100: '#D8F3DC',
          200: '#B7E4C7',
          300: '#95D5B2',
          400: '#74C69D',
          500: '#52B788',
          600: '#40916C',
          700: '#2D6A4F',  // Leaf Green - buttons, active links
          800: '#1B4332',  // Forest Green - nav, headings
          900: '#081C15',
          950: '#040D0A',
        },
        // Accent - Harvest Gold
        accent: {
          50: '#FFF8E1',
          100: '#FFECB3',
          200: '#FFE082',
          300: '#FFD54F',
          400: '#FFCA28',
          500: '#FFB703',  // Harvest Gold - main accent
          600: '#FFA000',
          700: '#FF8F00',
          800: '#FF6F00',
          900: '#E65100',
        },
        // Light backgrounds
        surface: {
          50: '#FFFFFF',
          100: '#F8F9FA',  // Clean White - main background
          200: '#D8F3DC',  // Mint Tint - cards, sections
          300: '#B7E4C7',
          400: '#E9ECEF',
          500: '#DEE2E6',
        },
        // Text colors
        text: {
          primary: '#1B4332',
          secondary: '#2D6A4F',
          muted: '#6C757D',
          light: '#ADB5BD',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        'soft': '0 2px 15px rgba(27, 67, 50, 0.08)',
        'medium': '0 4px 25px rgba(27, 67, 50, 0.12)',
        'card': '0 2px 8px rgba(27, 67, 50, 0.06)',
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
      },
    },
  },
  plugins: [],
};
