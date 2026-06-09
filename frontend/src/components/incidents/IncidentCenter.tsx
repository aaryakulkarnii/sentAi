"use client";

import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { incidentsApi } from "@/lib/api";
import { riskScoreColor } from "@/lib/utils";
import type { Incident } from "@/types";

const STATUS_COLOR: Record<string, string> = {
  open: "text-red-400 bg-red-400/10",
  investigating: "text-amber-400 bg-amber-400/10",
  contained: "text-blue-400 bg-blue-400/10",
  resolved: "text-green-400 bg-green-400/10",
  closed: "text-gray-400 bg-gray-400/10",
};

export default function IncidentCenter() {
  const { data: incidents = [] } = useQuery<Incident[]>({
    queryKey: ["incidents"],
    queryFn: () => incidentsApi.list().then((r) => r.data),
    refetchInterval: 20_000,
  });

  return (
    <main className="p-6 space-y-4">
      <h1 className="text-xl font-semibold text-white">Incidents</h1>
      <div className="space-y-2">
        {incidents.map((inc) => (
          <motion.div
            key={inc.id}
            initial={{ opacity: 0, x: -4 }}
            animate={{ opacity: 1, x: 0 }}
            className="bg-gray-900/60 border border-gray-800/50 rounded-xl px-5 py-4 flex items-center gap-4"
          >
            <div className="flex-1 min-w-0">
              <p className="font-medium text-white text-sm truncate">{inc.title}</p>
              <p className="text-xs text-gray-500 mt-0.5 font-mono">{inc.id.slice(0, 8)}…</p>
            </div>
            <span className={`px-2 py-0.5 rounded text-xs font-medium ${STATUS_COLOR[inc.status] ?? ""}`}>
              {inc.status}
            </span>
            <span className={`font-mono font-bold text-sm ${riskScoreColor(inc.risk_score)}`}>
              {inc.risk_score}
            </span>
          </motion.div>
        ))}
        {incidents.length === 0 && (
          <p className="text-center py-16 text-gray-600 text-sm">No incidents</p>
        )}
      </div>
    </main>
  );
}
