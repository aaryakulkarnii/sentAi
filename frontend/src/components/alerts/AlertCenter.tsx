"use client";

import { useQuery } from "@tanstack/react-query";
import { motion, AnimatePresence } from "framer-motion";
import { alertsApi } from "@/lib/api";
import { SEVERITY_COLOR } from "@/lib/utils";
import type { Alert } from "@/types";

export default function AlertCenter() {
  const { data: alerts = [], isLoading } = useQuery<Alert[]>({
    queryKey: ["alerts", "all"],
    queryFn: () => alertsApi.list({ limit: 200 }).then((r) => r.data),
    refetchInterval: 10_000,
  });

  return (
    <main className="p-6 space-y-4">
      <div>
        <h1 className="text-xl font-semibold text-white">Alert center</h1>
        <p className="text-sm text-gray-500 mt-0.5">{alerts.length} alerts</p>
      </div>

      <div className="bg-gray-900/60 border border-gray-800/50 rounded-xl overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-800/50 text-xs text-gray-500 uppercase tracking-wider">
              <th className="px-4 py-3 text-left">Severity</th>
              <th className="px-4 py-3 text-left">Description</th>
              <th className="px-4 py-3 text-left">Source IP</th>
              <th className="px-4 py-3 text-left">MITRE</th>
              <th className="px-4 py-3 text-left">Status</th>
              <th className="px-4 py-3 text-left">Time</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-800/30">
            <AnimatePresence>
              {alerts.map((a) => (
                <motion.tr
                  key={a.id}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="hover:bg-gray-800/20 transition-colors"
                >
                  <td className="px-4 py-3">
                    <span className={`px-2 py-0.5 rounded text-xs font-medium ${SEVERITY_COLOR[a.severity]}`}>
                      {a.severity}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-gray-300 max-w-xs truncate">{a.description}</td>
                  <td className="px-4 py-3 font-mono text-xs text-gray-400">{a.source_ip}</td>
                  <td className="px-4 py-3 font-mono text-xs text-purple-400">{a.mitre_technique_id}</td>
                  <td className="px-4 py-3">
                    <span className="text-xs text-gray-400">{a.status}</span>
                  </td>
                  <td className="px-4 py-3 text-xs text-gray-500 font-mono">
                    {new Date(a.created_at).toLocaleTimeString()}
                  </td>
                </motion.tr>
              ))}
            </AnimatePresence>
          </tbody>
        </table>
        {isLoading && <p className="text-center py-8 text-gray-600 text-sm">Loading alerts…</p>}
        {!isLoading && alerts.length === 0 && (
          <p className="text-center py-8 text-gray-600 text-sm">No alerts found</p>
        )}
      </div>
    </main>
  );
}
