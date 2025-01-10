/** @type {import('tailwindcss').Config} */

module.exports = {
  content: [
    "./src/frontend/templates/**/*.html",  // Include all HTML files in templates directory and subdirectories
    "./src/**/*.py",                       // Include all Python files
    "./src/frontend/static/**/*.js",       // Include all JavaScript files in static directory
  ],
  theme: {
    extend: {},
  },
  plugins: [],
};
