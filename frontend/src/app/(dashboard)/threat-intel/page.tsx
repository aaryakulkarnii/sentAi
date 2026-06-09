import { Metadata } from "next";
import ThreatIntelCenter from "@/components/threat-intel/ThreatIntelCenter";

export const metadata: Metadata = { title: "Threat Intelligence – SentinelAI" };

export default function ThreatIntelPage() {
  return <ThreatIntelCenter />;
}
