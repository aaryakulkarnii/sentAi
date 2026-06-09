import { Metadata } from "next";

export const metadata: Metadata = { title: "Reports – SentinelAI" };

export default function ReportsPage() {
  return (
    <main className="p-6">
      <h1 className="text-xl font-semibold text-white">Reports</h1>
      <p className="text-sm text-gray-500 mt-2">Report generation will be available in Phase 4.</p>
    </main>
  );
}
