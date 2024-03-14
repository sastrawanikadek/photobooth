/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: "selector",
  content: ["./client/**/*.{ts,tsx}"],
  prefix: "",
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: {
        "2xl": "1400px",
      },
    },
    extend: {
      keyframes: {
        "accordion-down": {
          from: { height: "0" },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: "0" },
        },
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
      },
      colors: {
        primary: {
          50: "#AE7FC7",
          100: "#A571C1",
          200: "#9C63BB",
          300: "#9355B4",
          400: "#894BAA",
          500: "#7B439A",
          600: "#723E8E",
          700: "#673880",
          800: "#5B3271",
          900: "#502C63",
        },
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
};
