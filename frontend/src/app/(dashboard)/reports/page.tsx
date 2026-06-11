"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { FileText, FileDown, Plus, Download, Loader2 } from "lucide-react";
import { PageHeader, EmptyState } from "@/components/ui";
import { reportsApi, incidentsApi } from "@/lib/api";

export default function ReportsPage() {
  const queryClient = useQueryClient();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedIncident, setSelectedIncident] = useState<string>("");
  const [selectedFormat, setSelectedFormat] = useState<string>("pdf");

  // Fetch reports
  const { data: reports, isLoading } = useQuery({
    queryKey: ["reports"],
    queryFn: async () => {
      const res = await reportsApi.list();
      return res.data;
    },
  });

  // Fetch incidents for the dropdown
  const { data: incidents } = useQuery({
    queryKey: ["incidents"],
    queryFn: async () => {
      const res = await incidentsApi.list();
      return res.data;
    },
    enabled: isModalOpen, // Only fetch when modal is open
  });

  const generateMutation = useMutation({
    mutationFn: () => reportsApi.generate(selectedIncident, selectedFormat),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["reports"] });
      setIsModalOpen(false);
      setSelectedIncident("");
      setSelectedFormat("pdf");
    },
  });

  return (
    <main className="mx-auto max-w-[1100px] space-y-6 p-6">
      <div className="flex items-center justify-between">
        <PageHeader
          title="Reports"
          subtitle="Generate executive-grade incident reports as PDF or DOCX"
          icon={<FileText size={17} />}
        />
        <button
          onClick={() => setIsModalOpen(true)}
          className="flex items-center gap-2 rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-blue-700"
        >
          <Plus size={16} />
          Generate Report
        </button>
      </div>

      {isLoading ? (
        <div className="flex justify-center p-12">
          <Loader2 className="animate-spin text-blue-500" size={32} />
        </div>
      ) : reports?.length === 0 ? (
        <EmptyState
          icon={<FileDown size={18} />}
          title="No reports generated yet"
          hint="Click 'Generate Report' to create your first incident report."
        />
      ) : (
        <div className="rounded-xl border border-white/10 bg-white/5 overflow-hidden">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="bg-white/5 text-xs uppercase text-slate-400">
              <tr>
                <th className="px-6 py-4 font-medium">Report ID</th>
                <th className="px-6 py-4 font-medium">Incident ID</th>
                <th className="px-6 py-4 font-medium">Format</th>
                <th className="px-6 py-4 font-medium">Date</th>
                <th className="px-6 py-4 font-medium text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/10">
              {reports?.map((report: any) => (
                <tr key={report.id} className="transition-colors hover:bg-white/5">
                  <td className="px-6 py-4 font-mono text-xs">{report.id.substring(0, 8)}...</td>
                  <td className="px-6 py-4 font-mono text-xs">{report.incident_id.substring(0, 8)}...</td>
                  <td className="px-6 py-4 uppercase font-semibold text-slate-200">{report.format}</td>
                  <td className="px-6 py-4 text-slate-400">
                    {new Date(report.created_at).toLocaleString()}
                  </td>
                  <td className="px-6 py-4 text-right">
                    <button
                      onClick={() => reportsApi.download(report.id)}
                      className="inline-flex items-center gap-1 text-blue-400 hover:text-blue-300 transition-colors"
                      title="Download"
                    >
                      <Download size={16} />
                      <span className="sr-only">Download</span>
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Generation Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
          <div className="w-full max-w-md rounded-xl border border-white/10 bg-slate-900 p-6 shadow-2xl">
            <h3 className="mb-4 text-lg font-semibold text-white">Generate Report</h3>
            
            <div className="space-y-4">
              <div>
                <label className="mb-1 block text-sm font-medium text-slate-400">Select Incident</label>
                <select
                  value={selectedIncident}
                  onChange={(e) => setSelectedIncident(e.target.value)}
                  className="w-full rounded-md border border-white/10 bg-black/50 p-2.5 text-sm text-white focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                >
                  <option value="">-- Choose an incident --</option>
                  {incidents?.map((inc: any) => (
                    <option key={inc.id} value={inc.id}>
                      {inc.title} ({inc.status})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="mb-1 block text-sm font-medium text-slate-400">Format</label>
                <div className="flex gap-4">
                  <label className="flex items-center gap-2 text-sm text-slate-300 cursor-pointer">
                    <input
                      type="radio"
                      name="format"
                      value="pdf"
                      checked={selectedFormat === "pdf"}
                      onChange={(e) => setSelectedFormat(e.target.value)}
                      className="text-blue-600 focus:ring-blue-500 bg-black border-white/20"
                    />
                    PDF
                  </label>
                  <label className="flex items-center gap-2 text-sm text-slate-300 cursor-pointer">
                    <input
                      type="radio"
                      name="format"
                      value="docx"
                      checked={selectedFormat === "docx"}
                      onChange={(e) => setSelectedFormat(e.target.value)}
                      className="text-blue-600 focus:ring-blue-500 bg-black border-white/20"
                    />
                    DOCX
                  </label>
                </div>
              </div>
            </div>

            <div className="mt-6 flex justify-end gap-3">
              <button
                onClick={() => setIsModalOpen(false)}
                className="rounded-md px-4 py-2 text-sm font-medium text-slate-300 hover:bg-white/5 transition-colors"
                disabled={generateMutation.isPending}
              >
                Cancel
              </button>
              <button
                onClick={() => generateMutation.mutate()}
                disabled={!selectedIncident || generateMutation.isPending}
                className="flex items-center gap-2 rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {generateMutation.isPending ? <Loader2 size={16} className="animate-spin" /> : <FileText size={16} />}
                Generate
              </button>
            </div>
          </div>
        </div>
      )}
    </main>
  );
}
