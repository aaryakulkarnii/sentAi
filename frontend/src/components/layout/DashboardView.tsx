"use client";

import { useQuery } from "@tanstack/react-query";
import { Activity, ShieldAlert, Siren, Gauge } from "lucide-react";
import { alertsApi, incidentsApi } from "@/lib/api";
import { cn, riskScoreColor, SEVERITY_DOT } from "@/lib/utils";
import { PageHeader, StatCard, Panel, Badge, EmptyState } from "@/components/ui";
import { SEVERITY_COLOR } from "@/lib/utils";
import type { Alert, Incident, Severity } from "@/types";

const SEVERITIES: Severity[] = ["critical", "high", "medium", "low"];

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

  const counts = SEVERITIES.map((s) => ({
    sev: s,
    n: alerts.filter((a) => a.severity === s).length,
  }));
  const maxN = Math.max(1, ...counts.map((c) => c.n));

  return (
    <main className="mx-auto max-w-[1400px] space-y-6 p-6">
      <PageHeader
        title="SOC Dashboard"
        subtitle="Real-time threat overview across your environment"
        actions={
          <Badge className="border border-white/10 bg-white/[0.03] text-ink-200" dot="bg-sev-ok">
            <span className="text-ink-300">Live</span>
          </Badge>
        }
      />

      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <StatCard label="Total alerts" value={alerts.length} sub="last 24h" index={0} />
        <StatCard
          label="Critical"
          value={critical}
          sub="requires action"
          accent={critical > 0 ? "text-sev-critical" : undefined}
          index={1}
        />
        <StatCard label="Open incidents" value={open} sub="unresolved" index={2} />
        <StatCard
          label="Avg risk score"
          value={avgRisk}
          sub="across incidents"
          accent={riskScoreColor(avgRisk)}
          index={3}
        />
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        {/* Recent alerts */}
        <Panel className="lg:col-span-2">
          <div className="flex items-center justify-between border-b border-white/[0.06] px-5 py-3.5">
            <h2 className="flex items-center gap-2 text-sm font-medium text-white">
              <Activity size={15} className="text-ink-400" />
              Recent alerts
            </h2>
            <span className="font-mono text-xs text-ink-500">{alerts.length}</span>
          </div>
          {alerts.length === 0 ? (
            <div className="p-5">
              <EmptyState
                icon={<ShieldAlert size={18} />}
                title="No alerts yet"
                hint="Detections will appear here in real time as events are ingested."
              />
            </div>
          ) : (
            <div className="divide-y divide-white/[0.04]">
              {alerts.slice(0, 8).map((a) => (
                <div
                  key={a.id}
                  className="flex items-center gap-3 px-5 py-3 text-sm transition-colors hover:bg-white/[0.02]"
                >
                  <span className={cn("h-1.5 w-1.5 flex-shrink-0 rounded-full", SEVERITY_DOT[a.severity])} />
                  <span className="flex-1 truncate text-ink-200">
                    {a.description ?? "No description"}
                  </span>
                  {a.source_ip && (
                    <span className="font-mono text-xs text-ink-500">{a.source_ip}</span>
                  )}
                  <Badge className={SEVERITY_COLOR[a.severity]}>{a.severity}</Badge>
                </div>
              ))}
            </div>
          )}
        </Panel>

        {/* Severity breakdown */}
        <Panel>
          <div className="flex items-center justify-between border-b border-white/[0.06] px-5 py-3.5">
            <h2 className="flex items-center gap-2 text-sm font-medium text-white">
              <Gauge size={15} className="text-ink-400" />
              Severity breakdown
            </h2>
          </div>
          <div className="space-y-4 p-5">
            {counts.map(({ sev, n }) => (
              <div key={sev}>
                <div className="mb-1.5 flex items-center justify-between text-xs">
                  <span className="flex items-center gap-2 capitalize text-ink-200">
                    <span className={cn("h-1.5 w-1.5 rounded-full", SEVERITY_DOT[sev])} />
                    {sev}
                  </span>
                  <span className="font-mono tabular-nums text-ink-400">{n}</span>
                </div>
                <div className="h-1.5 overflow-hidden rounded-full bg-white/[0.04]">
                  <div
                    className={cn("h-full rounded-full transition-all duration-500", SEVERITY_DOT[sev])}
                    style={{ width: `${(n / maxN) * 100}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </Panel>
      </div>
    </main>
  );
}
