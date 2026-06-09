"use client";

import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { alertsApi, incidentsApi } from "@/lib/api";
import { riskScoreColor, SEVERITY_COLOR } from "@/lib/utils";
import type { Alert, Incident } from "@/types";

const StatCard = ({ label, value, sub }: { label: string; value: string | number; sub?: string }) => (
  <motion.div
    initial={{ opacity: 0, y: 10 }}
    animate={{ opacity: 1, y: 0 }}
    className="bg-gray-900/60 border border-gray-800/50 rounded-xl p-5"
  >
    <p className="text-gray-500 text-xs font-medium uppercase tracking-wider">{label}</p>
    <p className="text-3xl font-bold font-mono text-white mt-2">{value}</p>
    {sub && <p className="text-xs text-gray-500 mt-1">{sub}</p>}
  </motion.div>
);

export default function DashboardView() {
  const { data: alerts = [] } = useQuery<Alert[]>({
    queryKey: ["alerts"],
    queryFn: () => alertsApi.list({ limit: 100 }).then((r) => r.data),
    refetchInterval: 15_000,
  });

  const { data: incidents = [] } = useQuery<Incident[]>({
    queryKey: ["incidents"],
    queryFn: () => incidentsApi.list().then((r) => r.data),
    refetchInterval: 30_000,
  });

  const critical = alerts.filter((a) => a.severity === "critical").length;
  const open = incidents.filter((i) => i.status === "open").length;
  const avgRisk = incidents.length
    ? Math.round(incidents.reduce((s, i) => s + i.risk_score, 0) / incidents.length)
    : 0;

  return (
    <main className="p-6 space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-white">SOC Dashboard</h1>
        <p className="text-sm text-gray-500 mt-0.5">Real-time threat overview</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard label="Total alerts" value={alerts.length} sub="last 24h" />
        <StatCard label="Critical" value={critical} sub="requires immediate action" />
        <StatCard label="Open incidents" value={open} />
        <StatCard label="Avg risk score" value={avgRisk} sub="across open incidents" />
      </div>

      {/* Recent alerts */}
      <div className="bg-gray-900/60 border border-gray-800/50 rounded-xl">
        <div className="px-5 py-4 border-b border-gray-800/50">
          <h2 className="text-sm font-semibold text-white">Recent alerts</h2>
        </div>
        <div className="divide-y divide-gray-800/30">
          {alerts.slice(0, 10).map((a) => (
            <div key={a.id} className="px-5 py-3 flex items-center gap-4 text-sm">
              <span className={`px-2 py-0.5 rounded text-xs font-medium ${SEVERITY_COLOR[a.severity]}`}>
                {a.severity}
              </span>
              <span className="text-gray-300 flex-1 truncate">{a.description ?? "No description"}</span>
              <span className="font-mono text-xs text-gray-500">{a.source_ip}</span>
            </div>
          ))}
          {alerts.length === 0 && (
            <p className="px-5 py-8 text-center text-gray-600 text-sm">No alerts yet</p>
          )}
        </div>
      </div>
    </main>
  );
}
