"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import {
  LayoutDashboard, UploadCloud, AlertTriangle, Siren, Server,
  Brain, Search, Shield, FileText, Settings, CornerDownLeft,
} from "lucide-react";
import { cn } from "@/lib/utils";

const COMMANDS = [
  { label: "Dashboard", href: "/dashboard", icon: LayoutDashboard, keywords: "home overview soc" },
  { label: "Ingest Logs", href: "/ingest", icon: UploadCloud, keywords: "csv upload import" },
  { label: "Alerts", href: "/alerts", icon: AlertTriangle, keywords: "detections" },
  { label: "Incidents", href: "/incidents", icon: Siren, keywords: "cases" },
  { label: "Assets", href: "/assets", icon: Server, keywords: "hosts inventory" },
  { label: "AI Investigate", href: "/investigate", icon: Brain, keywords: "agents investigation" },
  { label: "Threat Intel", href: "/threat-intel", icon: Search, keywords: "ioc lookup" },
  { label: "MITRE ATT&CK", href: "/mitre", icon: Shield, keywords: "matrix techniques" },
  { label: "Reports", href: "/reports", icon: FileText, keywords: "pdf export" },
  { label: "Settings", href: "/settings", icon: Settings, keywords: "account config" },
];

export default function CommandPalette({ open, onClose }: { open: boolean; onClose: () => void }) {
  const router = useRouter();
  const [query, setQuery] = useState("");
  const [active, setActive] = useState(0);

  const results = COMMANDS.filter(
    (c) =>
      c.label.toLowerCase().includes(query.toLowerCase()) ||
      c.keywords.includes(query.toLowerCase()),
  );

  useEffect(() => {
    if (open) {
      setQuery("");
      setActive(0);
    }
  }, [open]);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (!open) return;
      if (e.key === "Escape") onClose();
      if (e.key === "ArrowDown") {
        e.preventDefault();
        setActive((a) => Math.min(a + 1, results.length - 1));
      }
      if (e.key === "ArrowUp") {
        e.preventDefault();
        setActive((a) => Math.max(a - 1, 0));
      }
      if (e.key === "Enter" && results[active]) {
        router.push(results[active].href);
        onClose();
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, results, active, router, onClose]);

  return (
    <AnimatePresence>
      {open && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm"
          />
          <motion.div
            initial={{ opacity: 0, y: -8, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -8, scale: 0.98 }}
            className="fixed left-1/2 top-[18vh] z-50 w-full max-w-lg -translate-x-1/2 px-4"
          >
            <div className="panel overflow-hidden">
              <div className="relative flex items-center gap-2 border-b border-white/[0.06] px-4">
                <Search size={15} className="text-ink-400" />
                <input
                  autoFocus
                  value={query}
                  onChange={(e) => {
                    setQuery(e.target.value);
                    setActive(0);
                  }}
                  placeholder="Jump to…"
                  className="w-full bg-transparent py-3.5 text-sm text-white outline-none placeholder:text-ink-500"
                />
              </div>
              <div className="max-h-80 overflow-y-auto p-2">
                {results.map((c, i) => (
                  <button
                    key={c.href}
                    onMouseEnter={() => setActive(i)}
                    onClick={() => {
                      router.push(c.href);
                      onClose();
                    }}
                    className={cn(
                      "flex w-full items-center gap-3 rounded-lg px-3 py-2 text-left text-sm transition-colors",
                      i === active ? "bg-white/[0.07] text-white" : "text-ink-300",
                    )}
                  >
                    <c.icon size={15} className={i === active ? "text-white" : "text-ink-400"} />
                    {c.label}
                    {i === active && <CornerDownLeft size={13} className="ml-auto text-ink-500" />}
                  </button>
                ))}
                {results.length === 0 && (
                  <p className="px-3 py-6 text-center text-sm text-ink-500">No matches.</p>
                )}
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
