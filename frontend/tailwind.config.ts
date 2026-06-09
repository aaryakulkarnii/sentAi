import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        // Premium monochrome "ink" scale — near-black base, true-white top.
        ink: {
          950: "#08080a",
          900: "#0b0b0d",
          850: "#0f0f12",
          800: "#141417",
          700: "#1b1b1f",
          600: "#26262b",
          500: "#3a3a41",
          400: "#56565e",
          300: "#7c7c85",
          200: "#a8a8b0",
          100: "#d4d4d8",
          50: "#f4f4f5",
        },
        // Functional severity/status tokens — the only color allowed, reserved
        // for security semantics (used sparingly, low-saturation).
        sev: {
          critical: "#ff5c5c",
          high: "#ff9d4d",
          medium: "#ffd24d",
          low: "#6db8ff",
          ok: "#5ce0a0",
        },
      },
      fontFamily: {
        sans: ["var(--font-sans)", "Inter", "system-ui", "sans-serif"],
        mono: ["var(--font-mono)", "JetBrains Mono", "ui-monospace", "monospace"],
      },
      letterSpacing: {
        tightest: "-0.04em",
      },
      borderRadius: {
        xl: "0.875rem",
        "2xl": "1.125rem",
      },
      boxShadow: {
        // Layered premium shadow + subtle inset top highlight (glass edge).
        panel:
          "0 1px 0 0 rgba(255,255,255,0.04) inset, 0 1px 2px 0 rgba(0,0,0,0.4), 0 8px 24px -8px rgba(0,0,0,0.6)",
        "panel-hover":
          "0 1px 0 0 rgba(255,255,255,0.06) inset, 0 2px 4px 0 rgba(0,0,0,0.5), 0 16px 40px -12px rgba(0,0,0,0.7)",
        glow: "0 0 0 1px rgba(255,255,255,0.06), 0 0 40px -8px rgba(255,255,255,0.08)",
      },
      backgroundImage: {
        "glow-radial":
          "radial-gradient(60% 50% at 50% 0%, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0) 70%)",
        "panel-sheen":
          "linear-gradient(180deg, rgba(255,255,255,0.035) 0%, rgba(255,255,255,0) 40%)",
      },
      keyframes: {
        "fade-up": {
          "0%": { opacity: "0", transform: "translateY(6px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        shimmer: {
          "100%": { transform: "translateX(100%)" },
        },
        "pulse-soft": {
          "0%, 100%": { opacity: "1" },
          "50%": { opacity: "0.4" },
        },
      },
      animation: {
        "fade-up": "fade-up 0.4s cubic-bezier(0.16, 1, 0.3, 1)",
        shimmer: "shimmer 1.6s infinite",
        "pulse-soft": "pulse-soft 2.4s ease-in-out infinite",
      },
    },
  },
  plugins: [],
};

export default config;
