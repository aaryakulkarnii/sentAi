import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        // SentinelAI design tokens
        background: {
          primary: "hsl(var(--bg-primary) / <alpha-value>)",
          secondary: "hsl(var(--bg-secondary) / <alpha-value>)",
          tertiary: "hsl(var(--bg-tertiary) / <alpha-value>)",
        },
        sentinel: {
          cyan: "#00D4FF",
          green: "#00FF88",
          red: "#FF4444",
          amber: "#FFB800",
          purple: "#8B5CF6",
        },
      },
      fontFamily: {
        mono: ["JetBrains Mono", "Fira Code", "monospace"],
        sans: ["Inter", "system-ui", "sans-serif"],
      },
      animation: {
        "pulse-slow": "pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        "scan": "scan 2s linear infinite",
      },
      keyframes: {
        scan: {
          "0%": { transform: "translateY(-100%)" },
          "100%": { transform: "translateY(100%)" },
        },
      },
    },
  },
  plugins: [],
};

export default config;
