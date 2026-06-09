"use client";

import { useState } from "react";
import { Search, Globe } from "lucide-react";
import { threatIntelApi } from "@/lib/api";
import { cn } from "@/lib/utils";
import { PageHeader, Panel, Button, EmptyState } from "@/components/ui";

const VERDICT_COLOR: Record<string, string> = {
  malicious: "text-sev-critical bg-sev-critical/10 ring-sev-critical/20",
  suspicious: "text-sev-high bg-sev-high/10 ring-sev-high/20",
  clean: "text-sev-ok bg-sev-ok/10 ring-sev-ok/20",
  unknown: "text-ink-300 bg-white/[0.04] ring-white/10",
};

export default function ThreatIntelCenter() {
  const [query, setQuery] = useState("");
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const search = async () => {
    if (!query.trim()) return;
    setLoading(true);
    try {
      const { data } = await threatIntelApi.searchIoc(query.trim());
      setResult(data);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="mx-auto max-w-[900px] space-y-5 p-6">
      <PageHeader
        title="Threat Intelligence"
        subtitle="Look up an IP, domain, file hash, or CVE across multiple sources"
        icon={<Globe size={17} />}
      />

      <div className="flex gap-3">
        <div className="relative flex-1">
          <Search size={14} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-ink-400" />
          <input
            className="w-full rounded-lg border border-white/10 bg-white/[0.03] py-2.5 pl-10 pr-4 text-sm text-white outline-none focus:border-white/25"
            placeholder="8.8.8.8 · evil.com · <sha256> · CVE-2024-1234"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && search()}
          />
        </div>
        <Button variant="primary" loading={loading} onClick={search}>
          {!loading && <Search size={14} />} Search
        </Button>
      </div>

      {!result && (
        <EmptyState
          icon={<Globe size={18} />}
          title="No lookup yet"
          hint="Enter an indicator above to query threat intelligence sources."
        />
      )}

      {result && (
        <Panel className="p-5">
          <div className="mb-4 flex items-center gap-3">
            <span className="font-mono text-sm text-white">{result.ioc}</span>
            <span className="rounded-md bg-white/[0.05] px-2 py-0.5 text-xs uppercase tracking-wide text-ink-300">
              {result.type}
            </span>
            <span
              className={cn(
                "ml-auto rounded-md px-2.5 py-0.5 text-xs font-semibold capitalize ring-1 ring-inset",
                VERDICT_COLOR[result.verdict] ?? VERDICT_COLOR.unknown,
              )}
            >
              {result.verdict}
            </span>
          </div>

          <div className="space-y-2">
            {(result.sources ?? []).map((s: any, i: number) => (
              <div key={i} className="rounded-lg border border-white/[0.06] bg-white/[0.02] p-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-ink-100">{s.source}</span>
                  <span
                    className={cn(
                      "text-[0.66rem] uppercase tracking-wide",
                      s.status === "ok"
                        ? "text-sev-ok"
                        : s.status === "not_configured"
                          ? "text-ink-500"
                          : "text-sev-high",
                    )}
                  >
                    {s.status}
                  </span>
                </div>
                <div className="mt-1.5 flex flex-wrap gap-x-4 gap-y-1 text-xs text-ink-400">
                  {Object.entries(s)
                    .filter(([k]) => !["source", "status"].includes(k))
                    .map(([k, v]) => (
                      <span key={k}>
                        <span className="text-ink-500">{k}:</span>{" "}
                        <span className="text-ink-200">{String(v)}</span>
                      </span>
                    ))}
                </div>
              </div>
            ))}
            {(result.sources ?? []).length === 0 && (
              <p className="text-sm text-ink-500">No sources returned for this indicator type.</p>
            )}
          </div>

          <p className="mt-4 text-xs text-ink-500">
            Connectors marked <span className="text-ink-300">not_configured</span> activate once you set
            their API keys (ABUSEIPDB_API_KEY, OTX_API_KEY) in the backend .env.
          </p>
        </Panel>
      )}
    </main>
  );
}
