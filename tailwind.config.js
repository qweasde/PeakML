/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    './apps/**/*.py',
    './static/src/**/*.js',
  ],
  theme: {
    extend: {
      colors: {
        'bg-deep':  '#06060F',
        'bg-main':  '#0A0A1A',
        'surface':  '#0E0E22',
        'surface2': '#131328',
        'accent':   '#7F77DD',
        'text1':    '#ECEDF8',
        'text2':    '#8080A4',
        'text3':    '#4A4A68',
      },
      fontFamily: {
        heading: ['"Russo One"', 'sans-serif'],
        body:    ['"Chakra Petch"', 'system-ui', 'sans-serif'],
      },
      borderColor: {
        DEFAULT: 'rgba(127,119,221,0.16)',
        hover:   'rgba(127,119,221,0.38)',
      },
    },
  },
  plugins: [],
}
