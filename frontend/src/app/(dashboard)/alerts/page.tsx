import { Metadata } from "next";
import AlertCenter from "@/components/alerts/AlertCenter";

export const metadata: Metadata = { title: "Alert Center – SentinelAI" };

export default function AlertsPage() {
  return <AlertCenter />;
}
