"use client";

import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { FileText, Download, Plus, FileType2 } from "lucide-react";
import { incidentsApi, reportsApi } from "@/lib/api";
import { MOCK_AUTH, MOCK_TOKEN } from "@/lib/mockAuth";
import { cn } from "@/lib/utils";
import { PageHeader, Panel, Button, EmptyState } from "@/components/ui";
import type { Incident } from "@/types";

interface Report {
  id: string;
  incident_id: string;
  format: string;
  created_at: string;
}

export default function ReportsPage() {
  const qc = useQueryClient();
  const [incidentId, setIncidentId] = useState("");
  const [format, setFormat] = useState<"pdf" | "docx">("pdf");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const { data: incidents = [] } = useQuery<Incident[]>({
    queryKey: ["incidents"],
    queryFn: () => incidentsApi.list().then((r) => r.data),
  });
  const { data: reports = [] } = useQuery<Report[]>({
    queryKey: ["reports"],
    queryFn: () => reportsApi.list().then((r) => r.data),
  });

  const incidentTitle = (id: string) => incidents.find((i) => i.id === id)?.title ?? id.slice(0, 8);

  const generate = async () => {
    if (!incidentId) return;
    setBusy(true);
    setError("");
    try {
      await reportsApi.generate(incidentId, format);
      qc.invalidateQueries({ queryKey: ["reports"] });
    } catch (e: any) {
      setError(e?.response?.data?.detail ?? "Generation failed.");
    } finally {
      setBusy(false);
    }
  };

  const download = async (report: Report) => {
    const token = MOCK_AUTH ? MOCK_TOKEN : localStorage.getItem("sentinel_token");
    const res = await fetch(reportsApi.downloadUrl(report.id), {
      headers: { Authorization: `Bearer ${token}` },
    });
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `sentinelai_report_${report.id.slice(0, 8)}.${report.format}`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <main className="mx-auto max-w-[1100px] space-y-6 p-6">
      <PageHeader
        title="Reports"
        subtitle="Generate executive PDF / DOCX reports from investigated incidents"
        icon={<FileText size={17} />}
      />

      {/* Generate */}
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
          <div className="flex rounded-lg border border-white/10 p-0.5">
            {(["pdf", "docx"] as const).map((f) => (
              <button
                key={f}
                onClick={() => setFormat(f)}
                className={cn(
                  "rounded-md px-3 py-1.5 text-xs font-medium uppercase transition-colors",
                  format === f ? "bg-white/[0.08] text-white" : "text-ink-400 hover:text-ink-200",
                )}
              >
                {f}
              </button>
            ))}
          </div>
          <Button variant="primary" loading={busy} onClick={generate} disabled={!incidentId}>
            {!busy && <Plus size={14} />} Generate
          </Button>
        </div>
        {error && <p className="mt-3 text-sm text-sev-critical">{error}</p>}
      </Panel>

      {/* History */}
      {reports.length === 0 ? (
        <EmptyState
          icon={<FileText size={18} />}
          title="No reports yet"
          hint="Generate a report from an investigated incident above."
        />
      ) : (
        <Panel>
          <div className="divide-y divide-white/[0.04]">
            {reports.map((r) => (
              <motion.div
                key={r.id}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex items-center gap-4 px-5 py-3.5"
              >
                <div className="flex h-9 w-9 items-center justify-center rounded-lg border border-white/10 bg-white/[0.03] text-ink-200">
                  <FileType2 size={16} />
                </div>
                <div className="min-w-0 flex-1">
                  <p className="truncate text-sm font-medium text-ink-100">
                    {incidentTitle(r.incident_id)}
                  </p>
                  <p className="font-mono text-[0.7rem] text-ink-500">
                    {r.format.toUpperCase()} · {new Date(r.created_at).toLocaleString()}
                  </p>
                </div>
                <Button size="sm" variant="secondary" onClick={() => download(r)}>
                  <Download size={13} /> Download
                </Button>
              </motion.div>
            ))}
          </div>
        </Panel>
      )}
    </main>
  );
}
