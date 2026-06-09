import { Metadata } from "next";
import { Suspense } from "react";
import AIConsole from "@/components/investigate/AIConsole";

export const metadata: Metadata = { title: "AI Investigation – SentinelAI" };

export default function InvestigatePage() {
  return (
    <Suspense fallback={null}>
      <AIConsole />
    </Suspense>
  );
}
