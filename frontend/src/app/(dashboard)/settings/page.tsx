"use client";

import { useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { Settings as SettingsIcon, User, LogOut, Cpu, Globe, ShieldCheck, Database } from "lucide-react";
import { useAuthStore } from "@/stores/auth";
import { systemApi } from "@/lib/api";
import { cn } from "@/lib/utils";
import { PageHeader, Panel, Button } from "@/components/ui";

function StatusDot({ on }: { on: boolean }) {
  return (
    <span
      className={cn("h-2 w-2 rounded-full", on ? "bg-sev-ok" : "bg-ink-500")}
      title={on ? "configured" : "not configured"}
    />
  );
}

export default function SettingsPage() {
  const { user, clearAuth } = useAuthStore();
  const router = useRouter();

  const { data: cfg } = useQuery({
    queryKey: ["system-config"],
    queryFn: () => systemApi.config().then((r) => r.data),
  });

  const handleLogout = () => {
    clearAuth();
    router.replace("/login");
  };

  return (
    <main className="mx-auto max-w-[800px] space-y-6 p-6">
      <PageHeader title="Settings" subtitle="Manage your account and workspace" icon={<SettingsIcon size={17} />} />

      {/* Account */}
      <Panel className="p-5">
        <div className="mb-4 flex items-center gap-2 text-sm font-medium text-white">
          <User size={15} className="text-ink-400" /> Account
        </div>
        <div className="flex items-center gap-4">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-b from-white/20 to-white/[0.06] font-mono text-sm font-semibold text-white">
            {user?.email?.slice(0, 2).toUpperCase() ?? "AN"}
          </div>
          <div className="flex-1">
            <p className="text-sm text-white">{user?.email ?? "—"}</p>
            <p className="mt-0.5 text-xs uppercase tracking-wider text-ink-400">
              {user?.role ?? "tier2"} analyst
            </p>
          </div>
          <Button variant="danger" size="sm" onClick={handleLogout}>
            <LogOut size={13} /> Sign out
          </Button>
        </div>
      </Panel>

      {/* LLM */}
      <Panel className="p-5">
        <div className="mb-3 flex items-center justify-between">
          <div className="flex items-center gap-2 text-sm font-medium text-white">
            <Cpu size={15} className="text-ink-400" /> AI engine
          </div>
          <span className="rounded-md bg-white/[0.05] px-2 py-0.5 text-[0.66rem] uppercase tracking-wide text-ink-300">
            {cfg?.mode ?? "—"} mode
          </span>
        </div>
        <div className="grid grid-cols-2 gap-3 text-sm">
          <div className="rounded-lg border border-white/[0.06] bg-white/[0.02] p-3">
            <p className="text-xs text-ink-400">Provider · Model</p>
            <p className="mt-0.5 text-ink-100">{cfg?.llm?.provider} · <span className="font-mono text-xs">{cfg?.llm?.model}</span></p>
          </div>
          <div className="flex items-center gap-2 rounded-lg border border-white/[0.06] bg-white/[0.02] p-3">
            <StatusDot on={!!cfg?.llm?.configured} />
            <span className="text-ink-200">{cfg?.llm?.configured ? "API key configured" : "Using template fallback"}</span>
          </div>
        </div>
        {!cfg?.llm?.configured && (
          <p className="mt-3 text-xs text-ink-500">
            Set <span className="font-mono text-ink-300">GROQ_API_KEY</span> in the backend .env for real LLM-generated summaries.
          </p>
        )}
      </Panel>

      {/* Threat intel */}
      <Panel className="p-5">
        <div className="mb-3 flex items-center gap-2 text-sm font-medium text-white">
          <Globe size={15} className="text-ink-400" /> Threat intelligence sources
        </div>
        <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
          {[
            ["AbuseIPDB", cfg?.threat_intel?.abuseipdb],
            ["AlienVault OTX", cfg?.threat_intel?.otx],
            ["MalwareBazaar", cfg?.threat_intel?.malwarebazaar],
            ["NVD / CVE", cfg?.threat_intel?.nvd],
          ].map(([name, on]) => (
            <div key={name as string} className="flex items-center gap-2 rounded-lg border border-white/[0.06] bg-white/[0.02] px-3 py-2 text-xs">
              <StatusDot on={!!on} />
              <span className="text-ink-200">{name}</span>
            </div>
          ))}
        </div>
      </Panel>

      {/* Detection + storage */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
        <Panel className="p-5">
          <div className="mb-3 flex items-center gap-2 text-sm font-medium text-white">
            <ShieldCheck size={15} className="text-ink-400" /> Detection thresholds
          </div>
          <div className="space-y-2 text-sm">
            <Row label="Brute force" value={cfg?.detection?.brute_force_threshold} />
            <Row label="Port scan" value={cfg?.detection?.port_scan_threshold} />
            <Row label="Correlation window" value={cfg ? `${cfg.detection?.correlation_window_s}s` : undefined} />
          </div>
        </Panel>
        <Panel className="p-5">
          <div className="mb-3 flex items-center gap-2 text-sm font-medium text-white">
            <Database size={15} className="text-ink-400" /> Storage
          </div>
          <div className="space-y-2 text-sm">
            <Row label="Reports" value={cfg?.storage?.reports} />
            <Row label="Version" value={cfg?.version} />
          </div>
        </Panel>
      </div>
    </main>
  );
}

function Row({ label, value }: { label: string; value?: string | number }) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-ink-400">{label}</span>
      <span className="font-mono text-xs text-ink-100">{value ?? "—"}</span>
    </div>
  );
}
