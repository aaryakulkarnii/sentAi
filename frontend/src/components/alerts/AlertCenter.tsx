"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { motion, AnimatePresence } from "framer-motion";
import { AlertTriangle, ShieldAlert } from "lucide-react";
import { alertsApi } from "@/lib/api";
import { cn, SEVERITY_COLOR } from "@/lib/utils";
import { PageHeader, Panel, Badge, EmptyState, Skeleton } from "@/components/ui";
import type { Alert, Severity } from "@/types";

const FILTERS: (Severity | "all")[] = ["all", "critical", "high", "medium", "low"];

export default function AlertCenter() {
  const [filter, setFilter] = useState<Severity | "all">("all");
  const { data: alerts = [], isLoading } = useQuery<Alert[]>({
    queryKey: ["alerts", "all"],
    queryFn: () => alertsApi.list({ limit: 200 }).then((r) => r.data),
    refetchInterval: 10_000,
  });

  const filtered = filter === "all" ? alerts : alerts.filter((a) => a.severity === filter);

  return (
    <main className="mx-auto max-w-[1400px] space-y-5 p-6">
      <PageHeader
        title="Alert Center"
        subtitle={`${alerts.length} detections in the active window`}
        icon={<AlertTriangle size={17} />}
      />

      <div className="flex items-center gap-1.5">
        {FILTERS.map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={cn(
              "rounded-lg px-3 py-1.5 text-xs font-medium capitalize transition-colors",
              filter === f
                ? "bg-white/[0.08] text-white ring-1 ring-inset ring-white/15"
                : "text-ink-400 hover:bg-white/[0.04] hover:text-ink-200",
            )}
          >
            {f}
            {f !== "all" && (
              <span className="ml-1.5 font-mono text-[0.65rem] text-ink-500">
                {alerts.filter((a) => a.severity === f).length}
              </span>
            )}
          </button>
        ))}
      </div>

      <Panel>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-white/[0.06] text-left text-[0.68rem] uppercase tracking-wider text-ink-500">
                <th className="px-5 py-3 font-medium">Severity</th>
                <th className="px-5 py-3 font-medium">Description</th>
                <th className="px-5 py-3 font-medium">Source IP</th>
                <th className="px-5 py-3 font-medium">MITRE</th>
                <th className="px-5 py-3 font-medium">Status</th>
                <th className="px-5 py-3 text-right font-medium">Time</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/[0.04]">
              {isLoading &&
                Array.from({ length: 6 }).map((_, i) => (
                  <tr key={i}>
                    <td className="px-5 py-3.5"><Skeleton className="h-5 w-16" /></td>
                    <td className="px-5 py-3.5"><Skeleton className="h-4 w-64" /></td>
                    <td className="px-5 py-3.5"><Skeleton className="h-4 w-24" /></td>
                    <td className="px-5 py-3.5"><Skeleton className="h-4 w-16" /></td>
                    <td className="px-5 py-3.5"><Skeleton className="h-4 w-20" /></td>
                    <td className="px-5 py-3.5"><Skeleton className="ml-auto h-4 w-16" /></td>
                  </tr>
                ))}
              <AnimatePresence>
                {filtered.map((a) => (
                  <motion.tr
                    key={a.id}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="group transition-colors hover:bg-white/[0.02]"
                  >
                    <td className="px-5 py-3.5">
                      <Badge className={SEVERITY_COLOR[a.severity]}>{a.severity}</Badge>
                    </td>
                    <td className="max-w-md truncate px-5 py-3.5 text-ink-200">
                      {a.description ?? "—"}
                    </td>
                    <td className="px-5 py-3.5 font-mono text-xs text-ink-400">
                      {a.source_ip ?? "—"}
                    </td>
                    <td className="px-5 py-3.5 font-mono text-xs text-ink-300">
                      {a.mitre_technique_id ?? "—"}
                    </td>
                    <td className="px-5 py-3.5">
                      <span className="text-xs capitalize text-ink-300">
                        {a.status.replace("_", " ")}
                      </span>
                    </td>
                    <td className="px-5 py-3.5 text-right font-mono text-xs text-ink-500">
                      {new Date(a.created_at).toLocaleTimeString()}
                    </td>
                  </motion.tr>
                ))}
              </AnimatePresence>
            </tbody>
          </table>
        </div>

        {!isLoading && filtered.length === 0 && (
          <div className="p-5">
            <EmptyState
              icon={<ShieldAlert size={18} />}
              title={filter === "all" ? "No alerts found" : `No ${filter} alerts`}
              hint="Detections from the ingestion pipeline will stream in here automatically."
            />
          </div>
        )}
      </Panel>
    </main>
  );
}
