// eslint-disable-next-line @typescript-eslint/no-var-requires
const defaultTheme = require("tailwindcss/defaultTheme");

module.exports = {
  content: ["./index.html", "./src/**/*.vue", "./src/**/*.ts"],
  theme: {
    extend: {
      colors: {
        nanyu: {
          50: "#f6f1f8",
          100: "#ede4f1",
          200: "#dcc8e4",
          300: "#cbadd7",
          400: "#aa78bd",
          500: "#8943a3",
          600: "#6B2C91", // 主色：青莲紫
          700: "#562374",
          800: "#401a57",
          900: "#2b113a",
        },
      },
      fontFamily: {
        sans: ["Inter var", ...defaultTheme.fontFamily.sans],
      },
    },
  },
  plugins: [require("@tailwindcss/forms"), require("@tailwindcss/typography")],
};
