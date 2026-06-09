import { Metadata } from "next";
import MitreMatrix from "@/components/mitre/MitreMatrix";

export const metadata: Metadata = { title: "MITRE ATT&CK – SentinelAI" };

export default function MitrePage() {
  return <MitreMatrix />;
}
