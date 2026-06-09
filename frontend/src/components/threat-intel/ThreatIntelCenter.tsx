"use client";

import { useState } from "react";
import { Search, Globe } from "lucide-react";
import { threatIntelApi } from "@/lib/api";
import { PageHeader, Panel, Button, EmptyState } from "@/components/ui";

export default function ThreatIntelCenter() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<object | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSearch = async () => {
    if (!query.trim()) return;
    setLoading(true);
    try {
      const { data } = await threatIntelApi.searchIoc(query);
      setResults(data);
    } catch {
      setResults({ error: "Lookup failed — threat intel connectors not yet configured." });
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="mx-auto max-w-[1000px] space-y-6 p-6">
      <PageHeader
        title="Threat Intelligence"
        subtitle="Enrich indicators across AbuseIPDB, OTX, MalwareBazaar & NVD"
        icon={<Globe size={17} />}
      />

      <Panel className="p-5">
        <div className="flex gap-3">
          <div className="relative flex-1">
            <Search size={15} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-ink-400" />
            <input
              className="w-full rounded-lg border border-white/10 bg-white/[0.03] py-2.5 pl-10 pr-4 text-sm text-white placeholder:text-ink-400 outline-none transition-colors focus:border-white/25 focus:bg-white/[0.05]"
              placeholder="Search IP, domain, file hash, or CVE…"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSearch()}
            />
          </div>
          <Button variant="primary" onClick={handleSearch} loading={loading}>
            Search
          </Button>
        </div>
      </Panel>

      {results ? (
        <Panel className="p-5">
          <pre className="max-h-[28rem] overflow-auto rounded-lg border border-white/[0.06] bg-ink-950/60 p-4 font-mono text-xs leading-relaxed text-ink-300">
            {JSON.stringify(results, null, 2)}
          </pre>
        </Panel>
      ) : (
        <EmptyState
          icon={<Search size={18} />}
          title="Search an indicator"
          hint="Enter an IP, domain, hash, or CVE to fan out enrichment across all configured threat-intel sources."
        />
      )}
    </main>
  );
}
