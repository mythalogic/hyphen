/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{html,js,svelte,ts}'],
  theme: {
    extend: {
      colors: {
        'hyphen-ink': '#0F0E0D',
        'hyphen-paper': '#F7F5F0',
        'hyphen-resonance': '#4A3F8C',
        'hyphen-tone': '#C4573A',
        'hyphen-muted': '#9B998F',
        'hyphen-border': '#E2DED5'
      },
      fontFamily: {
        haiku: ['"Lora"', 'serif'],
        ui: ['"DM Sans"', 'sans-serif']
      }
    }
  },
  plugins: []
};
