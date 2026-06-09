"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { Siren, ChevronRight } from "lucide-react";
import { incidentsApi } from "@/lib/api";
import { cn, riskScoreColor, riskScoreLabel, STATUS_COLOR } from "@/lib/utils";
import { PageHeader, Panel, Badge, EmptyState } from "@/components/ui";
import IncidentDrawer from "@/components/incidents/IncidentDrawer";
import type { Incident } from "@/types";

export default function IncidentCenter() {
  const [selected, setSelected] = useState<Incident | null>(null);
  const { data: incidents = [] } = useQuery<Incident[]>({
    queryKey: ["incidents"],
    queryFn: () => incidentsApi.list().then((r) => r.data),
    refetchInterval: 20_000,
  });

  return (
    <main className="mx-auto max-w-[1400px] space-y-5 p-6">
      <PageHeader
        title="Incidents"
        subtitle={`${incidents.length} correlated incidents`}
        icon={<Siren size={17} />}
      />

      {incidents.length === 0 ? (
        <EmptyState
          icon={<Siren size={18} />}
          title="No incidents"
          hint="Correlated alert clusters will be promoted to incidents automatically."
        />
      ) : (
        <div className="space-y-2.5">
          {incidents.map((inc, i) => (
            <motion.div
              key={inc.id}
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.04 }}
            >
              <Panel hover className="cursor-pointer" onClick={() => setSelected(inc)}>
                <div className="flex items-center gap-4 px-5 py-4">
                  <div
                    className={cn(
                      "flex h-11 w-11 flex-shrink-0 flex-col items-center justify-center rounded-lg border font-mono",
                      inc.risk_score >= 80
                        ? "border-sev-critical/30 bg-sev-critical/10"
                        : inc.risk_score >= 60
                          ? "border-sev-high/30 bg-sev-high/10"
                          : "border-white/10 bg-white/[0.03]",
                    )}
                  >
                    <span className={cn("text-base font-semibold leading-none", riskScoreColor(inc.risk_score))}>
                      {inc.risk_score}
                    </span>
                    <span className="mt-0.5 text-[0.55rem] uppercase tracking-wide text-ink-500">risk</span>
                  </div>

                  <div className="min-w-0 flex-1">
                    <p className="truncate text-sm font-medium text-white">{inc.title}</p>
                    <div className="mt-1 flex items-center gap-2.5 text-xs text-ink-500">
                      <span className="font-mono">{inc.id.slice(0, 8)}</span>
                      <span className="text-ink-700">·</span>
                      <span>{riskScoreLabel(inc.risk_score)} severity</span>
                      {inc.assigned_to && (
                        <>
                          <span className="text-ink-700">·</span>
                          <span>assigned</span>
                        </>
                      )}
                    </div>
                  </div>

                  <Badge className={STATUS_COLOR[inc.status] ?? STATUS_COLOR.closed}>
                    {inc.status}
                  </Badge>
                  <ChevronRight size={16} className="text-ink-600" />
                </div>
              </Panel>
            </motion.div>
          ))}
        </div>
      )}

      <IncidentDrawer incident={selected} onClose={() => setSelected(null)} />
    </main>
  );
}
