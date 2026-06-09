"use client";

import { useRef, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { UploadCloud, FileSpreadsheet, Download, CheckCircle2, Loader2 } from "lucide-react";
import { ingestApi } from "@/lib/api";
import { MOCK_AUTH, MOCK_TOKEN } from "@/lib/mockAuth";
import { cn } from "@/lib/utils";
import { PageHeader, Panel, Button } from "@/components/ui";

interface IngestResult {
  filename: string;
  rows: number;
  alerts: number;
  detected_columns: string[];
}

export default function IngestPage() {
  const qc = useQueryClient();
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragging, setDragging] = useState(false);
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState<IngestResult | null>(null);
  const [error, setError] = useState("");

  const upload = async (file: File) => {
    setBusy(true);
    setError("");
    setResult(null);
    try {
      const { data } = await ingestApi.uploadCsv(file);
      setResult(data);
      qc.invalidateQueries({ queryKey: ["alerts"] });
      qc.invalidateQueries({ queryKey: ["incidents"] });
      qc.invalidateQueries({ queryKey: ["mitre-matrix"] });
    } catch (e: any) {
      setError(e?.response?.data?.detail ?? "Upload failed. Ensure it's a valid CSV.");
    } finally {
      setBusy(false);
    }
  };

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragging(false);
    const file = e.dataTransfer.files?.[0];
    if (file) void upload(file);
  };

  const downloadSample = () => {
    // Use a token-bearing fetch so the protected endpoint authorizes.
    const token = MOCK_AUTH ? MOCK_TOKEN : localStorage.getItem("sentinel_token");
    fetch(ingestApi.sampleUrl, { headers: { Authorization: `Bearer ${token}` } })
      .then((r) => r.blob())
      .then((blob) => {
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "sentinelai_sample_logs.csv";
        a.click();
        URL.revokeObjectURL(url);
      });
  };

  return (
    <main className="mx-auto max-w-[900px] space-y-6 p-6">
      <PageHeader
        title="Ingest Logs"
        subtitle="Upload a CSV of security logs — SentinelAI detects, correlates, and investigates"
        icon={<UploadCloud size={17} />}
        actions={
          <Button variant="secondary" size="sm" onClick={downloadSample}>
            <Download size={13} /> Sample CSV
          </Button>
        }
      />

      {/* Dropzone */}
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={onDrop}
        onClick={() => inputRef.current?.click()}
        className={cn(
          "dot-grid flex cursor-pointer flex-col items-center justify-center rounded-xl border border-dashed px-6 py-16 text-center transition-colors",
          dragging ? "border-white/30 bg-white/[0.04]" : "border-white/12 hover:border-white/20 hover:bg-white/[0.02]",
        )}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".csv"
          className="hidden"
          onChange={(e) => {
            const f = e.target.files?.[0];
            if (f) void upload(f);
          }}
        />
        <div className="mb-3 flex h-12 w-12 items-center justify-center rounded-xl border border-white/10 bg-white/[0.03] text-ink-200">
          {busy ? <Loader2 size={20} className="animate-spin" /> : <FileSpreadsheet size={20} />}
        </div>
        <p className="text-sm font-medium text-ink-100">
          {busy ? "Processing…" : "Drop a CSV here, or click to browse"}
        </p>
        <p className="mt-1 text-xs text-ink-400">
          Columns auto-detected: timestamp, source_ip, dest_ip, dest_port, user, host, action…
        </p>
      </div>

      {error && (
        <p className="rounded-lg border border-sev-critical/20 bg-sev-critical/10 px-3 py-2 text-sm text-sev-critical">
          {error}
        </p>
      )}

      {result && (
        <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}>
          <Panel className="p-5">
            <div className="mb-4 flex items-center gap-2">
              <CheckCircle2 size={16} className="text-sev-ok" />
              <h3 className="text-sm font-semibold text-white">Ingested {result.filename}</h3>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="rounded-lg border border-white/[0.06] bg-white/[0.02] p-4">
                <p className="text-[0.7rem] uppercase tracking-wider text-ink-400">Rows processed</p>
                <p className="mt-1 font-mono text-2xl font-semibold text-white">{result.rows}</p>
              </div>
              <div className="rounded-lg border border-white/[0.06] bg-white/[0.02] p-4">
                <p className="text-[0.7rem] uppercase tracking-wider text-ink-400">Alerts raised</p>
                <p
                  className={cn(
                    "mt-1 font-mono text-2xl font-semibold",
                    result.alerts > 0 ? "text-sev-high" : "text-white",
                  )}
                >
                  {result.alerts}
                </p>
              </div>
            </div>
            <div className="mt-4 flex flex-wrap gap-1.5">
              {result.detected_columns.map((c) => (
                <span key={c} className="rounded-md bg-white/[0.05] px-2 py-0.5 font-mono text-[0.66rem] text-ink-300">
                  {c}
                </span>
              ))}
            </div>
            <p className="mt-4 text-sm text-ink-400">
              {result.alerts > 0
                ? "Detections raised — check Alerts, then Incidents to run an AI investigation."
                : "No detections from this batch. Try the sample CSV to see the full flow."}
            </p>
          </Panel>
        </motion.div>
      )}
    </main>
  );
}
