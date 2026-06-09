"use client";

import { useEffect, useRef, useState } from "react";
import { useSearchParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { motion, AnimatePresence } from "framer-motion";
import { Brain, Play, Loader2, Check, ShieldAlert, Clock, Crosshair, FileText } from "lucide-react";
import { incidentsApi, investigationsApi } from "@/lib/api";
import { cn, riskScoreColor, riskScoreLabel } from "@/lib/utils";
import { PageHeader, Panel, Button, Badge, EmptyState } from "@/components/ui";
import type { Incident } from "@/types";

const AGENTS = [
  "Threat Hunter",
  "Threat Intel",
  "MITRE Mapper",
  "Investigator",
  "Response Advisor",
  "Executive Summary",
];

const VERDICT_COLOR: Record<string, string> = {
  malicious: "text-sev-critical bg-sev-critical/10 ring-sev-critical/20",
  suspicious: "text-sev-high bg-sev-high/10 ring-sev-high/20",
  clean: "text-sev-ok bg-sev-ok/10 ring-sev-ok/20",
  unknown: "text-ink-300 bg-white/[0.04] ring-white/10",
};

export default function AIConsole() {
  const params = useSearchParams();
  const [incidentId, setIncidentId] = useState(params.get("incident") ?? "");
  const [stage, setStage] = useState(-1); // -1 idle, 0..5 running, 6 done
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState("");
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const { data: incidents = [] } = useQuery<Incident[]>({
    queryKey: ["incidents"],
    queryFn: () => incidentsApi.list().then((r) => r.data),
  });

  // Auto-run if arriving with ?incident=… from the incident drawer.
  useEffect(() => {
    const fromUrl = params.get("incident");
    if (fromUrl) {
      setIncidentId(fromUrl);
      void run(fromUrl);
    }
    return () => {
      if (pollRef.current) clearInterval(pollRef.current);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const cleanup = (advance: ReturnType<typeof setInterval>) => {
    clearInterval(advance);
    if (pollRef.current) clearInterval(pollRef.current);
  };

  const run = async (id: string) => {
    if (!id.trim() || running) return;
    setRunning(true);
    setError("");
    setResult(null);
    setStage(0);

    try {
      await investigationsApi.trigger(id);
    } catch {
      setError("Could not start investigation — check the incident ID.");
      setRunning(false);
      setStage(-1);
      return;
    }

    let visual = 0;
    const advance = setInterval(() => {
      visual = Math.min(visual + 1, AGENTS.length - 1);
      setStage(visual);
    }, 650);

    pollRef.current = setInterval(async () => {
      try {
        const { data } = await investigationsApi.status(id);
        if (data.status === "complete") {
          cleanup(advance);
          const res = await investigationsApi.get(id);
          setStage(AGENTS.length);
          setResult(res.data);
          setRunning(false);
        } else if (data.status === "failed") {
          cleanup(advance);
          setError("Investigation failed. See server logs.");
          setRunning(false);
          setStage(-1);
        }
      } catch {
        /* keep polling */
      }
    }, 1000);
  };

  const timeline = result?.attack_timeline?.events ?? [];
  const mitre = result?.mitre_mappings ?? {};
  const iocs = result?.iocs?.items ?? [];
  const remediation = result?.remediation ?? {};
  const summary = remediation.executive_summary ?? "";

  return (
    <main className="mx-auto max-w-[1200px] space-y-6 p-6">
      <PageHeader
        title="AI Investigation Console"
        subtitle="Autonomous multi-agent investigation pipeline"
        icon={<Brain size={17} />}
      />

      {/* Trigger */}
      <Panel className="p-4">
        <div className="flex flex-col gap-3 sm:flex-row">
          <select
            value={incidentId}
            onChange={(e) => setIncidentId(e.target.value)}
            className="flex-1 rounded-lg border border-white/10 bg-white/[0.03] px-3.5 py-2.5 text-sm text-white outline-none focus:border-white/25"
          >
            <option value="">Select an incident…</option>
            {incidents.map((i) => (
              <option key={i.id} value={i.id} className="bg-ink-800">
                {i.title} · risk {i.risk_score}
              </option>
            ))}
          </select>
          <Button variant="primary" loading={running} onClick={() => run(incidentId)} disabled={!incidentId}>
            {!running && <Play size={14} />}
            {running ? "Investigating…" : "Run investigation"}
          </Button>
        </div>
        {error && <p className="mt-3 text-sm text-sev-critical">{error}</p>}
      </Panel>

      {/* Agent pipeline */}
      {stage >= 0 && (
        <Panel className="p-5">
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
            {AGENTS.map((agent, i) => {
              const done = stage > i;
              const active = stage === i && running;
              return (
                <div
                  key={agent}
                  className={cn(
                    "flex flex-col items-center gap-2 rounded-lg border p-3 text-center transition-colors",
                    done
                      ? "border-sev-ok/30 bg-sev-ok/[0.06]"
                      : active
                        ? "border-white/25 bg-white/[0.05]"
                        : "border-white/[0.06] bg-white/[0.01]",
                  )}
                >
                  <div
                    className={cn(
                      "flex h-7 w-7 items-center justify-center rounded-full text-xs",
                      done ? "bg-sev-ok/20 text-sev-ok" : active ? "bg-white/10 text-white" : "bg-white/[0.04] text-ink-500",
                    )}
                  >
                    {done ? <Check size={14} /> : active ? <Loader2 size={13} className="animate-spin" /> : i + 1}
                  </div>
                  <span className={cn("text-[0.68rem] font-medium", done || active ? "text-ink-100" : "text-ink-500")}>
                    {agent}
                  </span>
                </div>
              );
            })}
          </div>
        </Panel>
      )}

      {/* Result */}
      <AnimatePresence>
        {result && (
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">
            {/* Executive summary + risk */}
            <Panel className="p-5">
              <div className="flex items-start gap-4">
                <div
                  className={cn(
                    "flex h-14 w-14 flex-shrink-0 flex-col items-center justify-center rounded-xl border",
                    result.risk_score >= 60 ? "border-sev-high/30 bg-sev-high/10" : "border-white/10 bg-white/[0.03]",
                  )}
                >
                  <span className={cn("font-mono text-xl font-semibold", riskScoreColor(result.risk_score))}>
                    {result.risk_score}
                  </span>
                  <span className="text-[0.5rem] uppercase tracking-wide text-ink-500">risk</span>
                </div>
                <div>
                  <div className="mb-1 flex items-center gap-2">
                    <FileText size={14} className="text-ink-400" />
                    <h3 className="text-sm font-semibold text-white">Executive summary</h3>
                    <Badge className="bg-white/[0.05] text-ink-300">{riskScoreLabel(result.risk_score)}</Badge>
                  </div>
                  <p className="text-sm leading-relaxed text-ink-200">{summary}</p>
                </div>
              </div>
            </Panel>

            <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
              {/* Timeline */}
              <Panel className="p-5">
                <h3 className="mb-4 flex items-center gap-2 text-sm font-semibold text-white">
                  <Clock size={14} className="text-ink-400" /> Attack timeline
                </h3>
                <ol className="relative ml-1.5 space-y-4 border-l border-white/[0.08] pl-5">
                  {timeline.map((ev: any, i: number) => (
                    <li key={i} className="relative">
                      <span className="absolute -left-[1.43rem] top-1 h-2.5 w-2.5 rounded-full bg-white/60 ring-4 ring-ink-900" />
                      <div className="flex flex-wrap items-center gap-2">
                        {ev.technique_id && (
                          <span className="rounded bg-white/[0.06] px-1.5 py-0.5 font-mono text-[0.62rem] text-ink-200">
                            {ev.technique_id}
                          </span>
                        )}
                        {ev.tactic && <span className="text-[0.66rem] text-ink-400">{ev.tactic}</span>}
                      </div>
                      <p className="mt-1 text-sm text-ink-200">{ev.description ?? ev.technique ?? "—"}</p>
                      {ev.source_ip && <p className="font-mono text-[0.62rem] text-ink-500">src {ev.source_ip}</p>}
                    </li>
                  ))}
                  {timeline.length === 0 && <li className="text-sm text-ink-500">No events.</li>}
                </ol>
              </Panel>

              {/* MITRE + IOCs */}
              <div className="space-y-4">
                <Panel className="p-5">
                  <h3 className="mb-3 flex items-center gap-2 text-sm font-semibold text-white">
                    <Crosshair size={14} className="text-ink-400" /> MITRE techniques
                  </h3>
                  <div className="space-y-2">
                    {Object.values(mitre).map((m: any) => (
                      <div key={m.id} className="rounded-lg border border-white/[0.06] bg-white/[0.02] p-2.5">
                        <div className="flex items-center gap-2">
                          <span className="font-mono text-xs text-ink-100">{m.id}</span>
                          {m.tactic && <span className="text-[0.66rem] text-ink-400">· {m.tactic}</span>}
                        </div>
                        <p className="mt-0.5 text-xs text-ink-300">{m.technique}</p>
                      </div>
                    ))}
                    {Object.keys(mitre).length === 0 && <p className="text-sm text-ink-500">None mapped.</p>}
                  </div>
                </Panel>

                <Panel className="p-5">
                  <h3 className="mb-3 flex items-center gap-2 text-sm font-semibold text-white">
                    <ShieldAlert size={14} className="text-ink-400" /> Indicators (IOCs)
                  </h3>
                  <div className="space-y-1.5">
                    {iocs.map((ioc: any, i: number) => (
                      <div key={i} className="flex items-center justify-between gap-2 text-sm">
                        <span className="font-mono text-xs text-ink-200">{ioc.value}</span>
                        <span
                          className={cn(
                            "rounded-md px-2 py-0.5 text-xs font-medium capitalize ring-1 ring-inset",
                            VERDICT_COLOR[ioc.verdict] ?? VERDICT_COLOR.unknown,
                          )}
                        >
                          {ioc.verdict}
                        </span>
                      </div>
                    ))}
                    {iocs.length === 0 && <p className="text-sm text-ink-500">None.</p>}
                  </div>
                </Panel>
              </div>
            </div>

            {/* Remediation */}
            <Panel className="p-5">
              <h3 className="mb-3 text-sm font-semibold text-white">Recommended remediation</h3>
              {remediation.playbooks?.length > 0 && (
                <div className="mb-3 flex flex-wrap gap-1.5">
                  {remediation.playbooks.map((p: string) => (
                    <Badge key={p} className="bg-white/[0.05] text-ink-300">{p}</Badge>
                  ))}
                </div>
              )}
              <ul className="space-y-1.5">
                {(remediation.ai_recommended ?? remediation.immediate_actions ?? []).map((step: string, i: number) => (
                  <li key={i} className="flex gap-2 text-sm text-ink-200">
                    <span className="mt-0.5 text-ink-500">→</span> {step}
                  </li>
                ))}
              </ul>
            </Panel>
          </motion.div>
        )}
      </AnimatePresence>

      {stage < 0 && !result && (
        <EmptyState
          icon={<Brain size={18} />}
          title="No investigation running"
          hint="Select an incident and run the autonomous 6-agent investigation pipeline."
        />
      )}
    </main>
  );
}
