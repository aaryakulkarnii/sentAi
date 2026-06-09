import { Metadata } from "next";
import AIConsole from "@/components/investigate/AIConsole";

export const metadata: Metadata = { title: "AI Investigation – SentinelAI" };

export default function InvestigatePage() {
  return <AIConsole />;
}
