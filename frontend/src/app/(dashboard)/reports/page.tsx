"use client";

import { FileText, FileDown } from "lucide-react";
import { PageHeader, EmptyState } from "@/components/ui";

export default function ReportsPage() {
  return (
    <main className="mx-auto max-w-[1100px] space-y-6 p-6">
      <PageHeader
        title="Reports"
        subtitle="Generate executive-grade incident reports as PDF or DOCX"
        icon={<FileText size={17} />}
      />
      <EmptyState
        icon={<FileDown size={18} />}
        title="No reports generated yet"
        hint="On-demand PDF/DOCX report generation arrives in Phase 4. Generated reports will be archived here with download history."
      />
    </main>
  );
}
