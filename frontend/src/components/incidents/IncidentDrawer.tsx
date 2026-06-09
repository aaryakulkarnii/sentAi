"use client";

import { useRouter } from "next/navigation";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { motion, AnimatePresence } from "framer-motion";
import { X, ArrowUpRight, Clock, Brain } from "lucide-react";
import { incidentsApi } from "@/lib/api";
import { cn, riskScoreColor, riskScoreLabel, SEVERITY_DOT, STATUS_COLOR } from "@/lib/utils";
import { Badge, Button } from "@/components/ui";
import type { Alert, Incident, TimelineEvent } from "@/types";

const NEXT_STATUS: Record<string, string[]> = {
  open: ["investigating", "contained", "closed"],
  investigating: ["contained", "resolved", "closed"],
  contained: ["resolved", "closed"],
  resolved: ["closed"],
  closed: [],
};

export default function IncidentDrawer({
  incident,
  onClose,
}: {
  incident: Incident | null;
  onClose: () => void;
}) {
  const qc = useQueryClient();
  const router = useRouter();
  const id = incident?.id;

  const { data: timeline = [] } = useQuery<TimelineEvent[]>({
    queryKey: ["incident", id, "timeline"],
    queryFn: () => incidentsApi.timeline(id!).then((r) => r.data),
    enabled: !!id,
  });
  const { data: alerts = [] } = useQuery<Alert[]>({
    queryKey: ["incident", id, "alerts"],
    queryFn: () => incidentsApi.alerts(id!).then((r) => r.data),
    enabled: !!id,
  });

  const refresh = () => {
    qc.invalidateQueries({ queryKey: ["incidents"] });
    qc.invalidateQueries({ queryKey: ["incident", id] });
  };

  const setStatus = async (status: string) => {
    if (!id) return;
    await incidentsApi.changeStatus(id, status);
    refresh();
  };
  const escalate = async () => {
    if (!id) return;
    await incidentsApi.escalate(id);
    refresh();
  };

  return (
    <AnimatePresence>
      {incident && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 z-30 bg-black/50 backdrop-blur-sm"
          />
          <motion.aside
            initial={{ x: "100%" }}
            animate={{ x: 0 }}
            exit={{ x: "100%" }}
            transition={{ type: "spring", stiffness: 360, damping: 38 }}
            className="fixed right-0 top-0 z-40 flex h-screen w-full max-w-xl flex-col border-l border-white/[0.08] bg-ink-900/95 backdrop-blur-xl"
          >
            {/* Header */}
            <div className="flex items-start gap-3 border-b border-white/[0.06] p-5">
              <div
                className={cn(
                  "flex h-12 w-12 flex-shrink-0 flex-col items-center justify-center rounded-lg border font-mono",
                  incident.risk_score >= 80
                    ? "border-sev-critical/30 bg-sev-critical/10"
                    : incident.risk_score >= 60
                      ? "border-sev-high/30 bg-sev-high/10"
                      : "border-white/10 bg-white/[0.03]",
                )}
              >
                <span className={cn("text-lg font-semibold leading-none", riskScoreColor(incident.risk_score))}>
                  {incident.risk_score}
                </span>
                <span className="mt-0.5 text-[0.5rem] uppercase tracking-wide text-ink-500">risk</span>
              </div>
              <div className="min-w-0 flex-1">
                <h2 className="text-sm font-semibold text-white">{incident.title}</h2>
                <div className="mt-1 flex items-center gap-2">
                  <Badge className={STATUS_COLOR[incident.status] ?? STATUS_COLOR.closed}>
                    {incident.status}
                  </Badge>
                  <span className="font-mono text-[0.7rem] text-ink-500">{incident.id.slice(0, 8)}</span>
                  <span className="text-[0.7rem] text-ink-500">· {riskScoreLabel(incident.risk_score)}</span>
                </div>
              </div>
              <button onClick={onClose} className="rounded-lg p-1.5 text-ink-400 hover:bg-white/[0.06] hover:text-white">
                <X size={16} />
              </button>
            </div>

            {/* Lifecycle controls */}
            <div className="flex flex-wrap items-center gap-2 border-b border-white/[0.06] px-5 py-3">
              <span className="mr-1 text-[0.7rem] uppercase tracking-wider text-ink-500">Move to</span>
              {(NEXT_STATUS[incident.status] ?? []).map((s) => (
                <Button key={s} size="sm" variant="secondary" onClick={() => setStatus(s)}>
                  {s}
                </Button>
              ))}
              {incident.status === "open" && (
                <Button size="sm" variant="secondary" onClick={escalate}>
                  <ArrowUpRight size={13} /> Escalate
                </Button>
              )}
              <Button
                size="sm"
                variant="primary"
                className="ml-auto"
                onClick={() => router.push(`/investigate?incident=${incident.id}`)}
              >
                <Brain size={13} /> Investigate with AI
              </Button>
            </div>

            <div className="flex-1 space-y-6 overflow-y-auto p-5">
              {/* Attack timeline */}
              <section>
                <h3 className="mb-3 flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-ink-400">
                  <Clock size={13} /> Attack timeline
                </h3>
                <ol className="relative ml-1.5 space-y-4 border-l border-white/[0.08] pl-5">
                  {timeline.map((ev, i) => (
                    <li key={i} className="relative">
                      <span
                        className={cn(
                          "absolute -left-[1.43rem] top-1 h-2.5 w-2.5 rounded-full ring-4 ring-ink-900",
                          SEVERITY_DOT[ev.severity as keyof typeof SEVERITY_DOT] ?? "bg-ink-400",
                        )}
                      />
                      <div className="flex items-center gap-2">
                        {ev.technique_id && (
                          <span className="font-mono text-[0.66rem] text-ink-300">{ev.technique_id}</span>
                        )}
                        <span className="font-mono text-[0.62rem] text-ink-500">
                          {new Date(ev.timestamp).toLocaleString()}
                        </span>
                      </div>
                      <p className="mt-0.5 text-sm text-ink-200">{ev.description ?? "—"}</p>
                      {ev.source_ip && (
                        <p className="font-mono text-[0.66rem] text-ink-500">src {ev.source_ip}</p>
                      )}
                    </li>
                  ))}
                  {timeline.length === 0 && <li className="text-sm text-ink-500">No timeline events.</li>}
                </ol>
              </section>

              {/* Member alerts */}
              <section>
                <h3 className="mb-3 text-xs font-semibold uppercase tracking-wider text-ink-400">
                  Correlated alerts ({alerts.length})
                </h3>
                <div className="space-y-1.5">
                  {alerts.map((a) => (
                    <div
                      key={a.id}
                      className="flex items-center gap-3 rounded-lg border border-white/[0.06] bg-white/[0.02] px-3 py-2 text-sm"
                    >
                      <span className={cn("h-1.5 w-1.5 rounded-full", SEVERITY_DOT[a.severity])} />
                      <span className="flex-1 truncate text-ink-200">{a.description}</span>
                      {a.mitre_technique_id && (
                        <span className="font-mono text-[0.66rem] text-ink-400">{a.mitre_technique_id}</span>
                      )}
                    </div>
                  ))}
                </div>
              </section>
            </div>
          </motion.aside>
        </>
      )}
    </AnimatePresence>
  );
}
