"use client";

import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { Shield } from "lucide-react";
import { mitreApi } from "@/lib/api";
import { cn } from "@/lib/utils";
import { PageHeader, EmptyState, StatCard } from "@/components/ui";
import type { MitreMatrix as Matrix, MatrixTechnique } from "@/types";

function techHeat(t: MatrixTechnique): string {
  if (!t.covered) return "border-white/[0.05] bg-white/[0.01] text-ink-400 hover:bg-white/[0.03]";
  if (t.alert_count >= 5)
    return "border-sev-critical/40 bg-sev-critical/15 text-sev-critical hover:bg-sev-critical/20";
  if (t.alert_count >= 2)
    return "border-sev-high/40 bg-sev-high/15 text-sev-high hover:bg-sev-high/20";
  return "border-sev-medium/40 bg-sev-medium/12 text-sev-medium hover:bg-sev-medium/20";
}

export default function MitreMatrix() {
  const { data } = useQuery<Matrix>({
    queryKey: ["mitre-matrix"],
    queryFn: () => mitreApi.matrix().then((r) => r.data),
    refetchInterval: 30_000,
  });

  const tactics = data?.tactics ?? [];

  return (
    <main className="mx-auto max-w-[1600px] space-y-5 p-6">
      <PageHeader
        title="MITRE ATT&CK Matrix"
        subtitle="Detection coverage across the attack lifecycle"
        icon={<Shield size={17} />}
      />

      {tactics.length === 0 ? (
        <EmptyState
          icon={<Shield size={18} />}
          title="MITRE data not loaded"
          hint={
            <>
              Run <code className="rounded bg-white/[0.06] px-1.5 py-0.5 font-mono text-ink-200">python -m scripts.dev_bootstrap</code> to seed the ATT&CK matrix.
            </>
          }
        />
      ) : (
        <>
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-3">
            <StatCard label="Tactics" value={tactics.length} index={0} />
            <StatCard label="Techniques tracked" value={data?.total_techniques ?? 0} index={1} />
            <StatCard
              label="Covered by alerts"
              value={data?.covered_techniques ?? 0}
              accent={data?.covered_techniques ? "text-sev-medium" : undefined}
              index={2}
            />
          </div>

          <div className="flex items-center gap-4 text-xs text-ink-400">
            <span className="font-medium uppercase tracking-wider text-ink-500">Coverage</span>
            {[
              ["bg-white/[0.04]", "none"],
              ["bg-sev-medium/40", "1 alert"],
              ["bg-sev-high/40", "2+"],
              ["bg-sev-critical/50", "5+"],
            ].map(([c, l]) => (
              <span key={l} className="flex items-center gap-1.5">
                <span className={cn("h-2.5 w-2.5 rounded-sm", c)} />
                {l}
              </span>
            ))}
          </div>

          <div className="flex gap-3 overflow-x-auto pb-3">
            {tactics.map((tactic, ti) => (
              <motion.div
                key={tactic.name}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: ti * 0.025 }}
                className="flex w-[180px] flex-shrink-0 flex-col"
              >
                <div className="mb-2 px-1">
                  <p className="truncate text-xs font-semibold text-white" title={tactic.name}>
                    {tactic.name}
                  </p>
                  <p className="font-mono text-[0.6rem] text-ink-500">
                    {tactic.id ?? "—"} · {tactic.techniques.length}
                  </p>
                </div>
                <div className="space-y-1.5">
                  {tactic.techniques.map((t) => (
                    <div
                      key={t.id}
                      title={`${t.id} ${t.technique}${t.covered ? ` · ${t.alert_count} alert(s)` : ""}`}
                      className={cn(
                        "cursor-default rounded-md border px-2 py-1.5 transition-colors",
                        techHeat(t),
                      )}
                    >
                      <div className="flex items-center justify-between gap-1">
                        <span className="truncate font-mono text-[0.62rem]">{t.id}</span>
                        {t.alert_count > 0 && (
                          <span className="rounded bg-black/30 px-1 font-mono text-[0.58rem]">
                            {t.alert_count}
                          </span>
                        )}
                      </div>
                      <p className="mt-0.5 truncate text-[0.66rem] leading-tight opacity-90">
                        {t.sub_technique ?? t.technique}
                      </p>
                    </div>
                  ))}
                </div>
              </motion.div>
            ))}
          </div>
        </>
      )}
    </main>
  );
}
