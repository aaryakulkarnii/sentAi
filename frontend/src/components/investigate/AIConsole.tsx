"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Brain, Play, CheckCircle2, Circle, Loader2 } from "lucide-react";
import { investigationsApi } from "@/lib/api";
import { cn, riskScoreColor } from "@/lib/utils";
import { PageHeader, Panel, Input, Button, EmptyState } from "@/components/ui";
import type { Investigation } from "@/types";

const AGENTS = [
  "Threat Hunter",
  "Threat Intel",
  "MITRE Mapper",
  "Investigator",
  "Response Advisor",
  "Executive Summary",
];

export default function AIConsole() {
  const [incidentId, setIncidentId] = useState("");
  const [investigation, setInvestigation] = useState<Investigation | null>(null);
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState(-1);

  const handleTrigger = async () => {
    if (!incidentId.trim()) return;
    setLoading(true);
    setInvestigation(null);
    setStep(0);

    // Animate agent pipeline progress while the backend works.
    const timer = setInterval(() => setStep((s) => Math.min(s + 1, AGENTS.length - 1)), 700);

    try {
      await investigationsApi.trigger(incidentId);
      await new Promise((res) => setTimeout(res, 3000));
      const { data } = await investigationsApi.get(incidentId);
      setInvestigation(data);
    } catch (err) {
      console.error(err);
    } finally {
      clearInterval(timer);
      setStep(AGENTS.length);
      setLoading(false);
    }
  };

  return (
    <main className="mx-auto max-w-[1100px] space-y-6 p-6">
      <PageHeader
        title="AI Investigation Console"
        subtitle="Multi-agent autonomous investigation pipeline"
        icon={<Brain size={17} />}
      />

      <Panel className="p-5">
        <div className="flex gap-3">
          <Input
            placeholder="Enter incident ID to investigate…"
            value={incidentId}
            onChange={(e) => setIncidentId(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleTrigger()}
          />
          <Button variant="primary" onClick={handleTrigger} loading={loading} disabled={!incidentId}>
            {!loading && <Play size={14} />}
            Investigate
          </Button>
        </div>
      </Panel>

      {/* Agent pipeline */}
      {step >= 0 && (
        <Panel className="p-5">
          <p className="mb-4 text-xs font-medium uppercase tracking-wider text-ink-400">
            Agent pipeline
          </p>
          <div className="grid grid-cols-2 gap-2.5 md:grid-cols-3">
            {AGENTS.map((agent, i) => {
              const done = step > i;
              const active = step === i && loading;
              return (
                <div
                  key={agent}
                  className={cn(
                    "flex items-center gap-2.5 rounded-lg border px-3 py-2.5 text-sm transition-all",
                    done
                      ? "border-sev-ok/20 bg-sev-ok/[0.06] text-ink-100"
                      : active
                        ? "border-white/15 bg-white/[0.05] text-white"
                        : "border-white/[0.06] bg-white/[0.01] text-ink-500",
                  )}
                >
                  {done ? (
                    <CheckCircle2 size={15} className="text-sev-ok" />
                  ) : active ? (
                    <Loader2 size={15} className="animate-spin text-white" />
                  ) : (
                    <Circle size={15} className="text-ink-600" />
                  )}
                  {agent}
                </div>
              );
            })}
          </div>
        </Panel>
      )}

      <AnimatePresence>
        {investigation && (
          <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}>
            <Panel className="p-5">
              <div className="mb-4 flex items-center justify-between">
                <h2 className="text-sm font-medium text-white">Investigation result</h2>
                <span className={cn("font-mono text-sm font-semibold", riskScoreColor(investigation.risk_score))}>
                  Risk {investigation.risk_score}
                </span>
              </div>
              <pre className="max-h-96 overflow-auto rounded-lg border border-white/[0.06] bg-ink-950/60 p-4 font-mono text-xs leading-relaxed text-ink-300">
                {JSON.stringify(investigation, null, 2)}
              </pre>
            </Panel>
          </motion.div>
        )}
      </AnimatePresence>

      {step < 0 && (
        <EmptyState
          icon={<Brain size={18} />}
          title="No active investigation"
          hint="Enter an incident ID above to launch the six-agent investigation pipeline."
        />
      )}
    </main>
  );
}
