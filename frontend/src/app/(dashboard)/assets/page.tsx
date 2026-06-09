"use client";

import { useQuery } from "@tanstack/react-query";
import { Server, ShieldCheck } from "lucide-react";
import { assetsApi } from "@/lib/api";
import { cn } from "@/lib/utils";
import { PageHeader, Panel, EmptyState } from "@/components/ui";
import type { Asset } from "@/types";

const CRIT_COLOR: Record<number, string> = {
  5: "text-sev-critical bg-sev-critical/10 ring-sev-critical/20",
  4: "text-sev-high bg-sev-high/10 ring-sev-high/20",
  3: "text-sev-medium bg-sev-medium/10 ring-sev-medium/20",
  2: "text-sev-low bg-sev-low/10 ring-sev-low/20",
  1: "text-ink-300 bg-white/[0.04] ring-white/10",
};

const CRIT_LABEL: Record<number, string> = {
  5: "Critical", 4: "High", 3: "Medium", 2: "Low", 1: "Minimal",
};

export default function AssetsPage() {
  const { data: assets = [] } = useQuery<Asset[]>({
    queryKey: ["assets"],
    queryFn: () => assetsApi.list().then((r) => r.data),
  });

  return (
    <main className="mx-auto max-w-[1400px] space-y-5 p-6">
      <PageHeader
        title="Asset Registry"
        subtitle={`${assets.length} monitored assets · criticality drives incident risk`}
        icon={<Server size={17} />}
      />

      {assets.length === 0 ? (
        <EmptyState icon={<ShieldCheck size={18} />} title="No assets registered" />
      ) : (
        <Panel>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-white/[0.06] text-left text-[0.68rem] uppercase tracking-wider text-ink-500">
                  <th className="px-5 py-3 font-medium">Hostname</th>
                  <th className="px-5 py-3 font-medium">IP</th>
                  <th className="px-5 py-3 font-medium">OS</th>
                  <th className="px-5 py-3 font-medium">Owner</th>
                  <th className="px-5 py-3 font-medium">Criticality</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.04]">
                {assets.map((a) => (
                  <tr key={a.id} className="transition-colors hover:bg-white/[0.02]">
                    <td className="px-5 py-3.5 font-medium text-white">{a.hostname}</td>
                    <td className="px-5 py-3.5 font-mono text-xs text-ink-400">{a.ip ?? "—"}</td>
                    <td className="px-5 py-3.5 text-ink-300">{a.os ?? "—"}</td>
                    <td className="px-5 py-3.5 text-ink-400">{a.owner ?? "—"}</td>
                    <td className="px-5 py-3.5">
                      <span
                        className={cn(
                          "inline-flex items-center gap-1.5 rounded-md px-2 py-0.5 text-xs font-medium ring-1 ring-inset",
                          CRIT_COLOR[a.criticality] ?? CRIT_COLOR[3],
                        )}
                      >
                        {CRIT_LABEL[a.criticality] ?? a.criticality} · {a.criticality}/5
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Panel>
      )}
    </main>
  );
}
