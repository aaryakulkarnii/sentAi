import { Metadata } from "next";
import IncidentCenter from "@/components/incidents/IncidentCenter";

export const metadata: Metadata = { title: "Incidents – SentinelAI" };

export default function IncidentsPage() {
  return <IncidentCenter />;
}
