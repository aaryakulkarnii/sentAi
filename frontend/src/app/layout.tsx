import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import Providers from "@/components/layout/Providers";

const inter = Inter({ subsets: ["latin"], variable: "--font-sans", display: "swap" });
const jetbrains = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-mono",
  display: "swap",
});

export const metadata: Metadata = {
  title: "SentinelAI – Autonomous SOC",
  description: "AI-powered Security Operations Center",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body
        className={`${inter.variable} ${jetbrains.variable} bg-ink-950 font-sans text-ink-100 antialiased`}
      >
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
