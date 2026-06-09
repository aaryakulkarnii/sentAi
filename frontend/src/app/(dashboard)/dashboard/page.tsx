import { Metadata } from "next";
import DashboardView from "@/components/layout/DashboardView";

export const metadata: Metadata = { title: "SOC Dashboard – SentinelAI" };

export default function DashboardPage() {
  return <DashboardView />;
}
