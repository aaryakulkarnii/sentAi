"use client";

import { useEffect, useState } from "react";
import { usePathname } from "next/navigation";
import { Search, Command } from "lucide-react";
import { useAuthStore } from "@/stores/auth";
import CommandPalette from "@/components/layout/CommandPalette";

const TITLES: Record<string, string> = {
  dashboard: "Dashboard",
  ingest: "Ingest Logs",
  alerts: "Alerts",
  incidents: "Incidents",
  assets: "Assets",
  investigate: "AI Investigate",
  "threat-intel": "Threat Intel",
  mitre: "MITRE ATT&CK",
  reports: "Reports",
  settings: "Settings",
};

export default function Topbar() {
  const pathname = usePathname();
  const user = useAuthStore((s) => s.user);
  const segment = pathname.split("/").filter(Boolean)[0] ?? "dashboard";
  const crumb = TITLES[segment] ?? "SentinelAI";
  const [paletteOpen, setPaletteOpen] = useState(false);

  const initials = user?.email?.slice(0, 2).toUpperCase() ?? "AN";

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        setPaletteOpen(true);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  return (
    <>
    <CommandPalette open={paletteOpen} onClose={() => setPaletteOpen(false)} />
    <header className="sticky top-0 z-20 flex h-14 items-center gap-4 border-b border-white/[0.06] bg-ink-950/70 px-6 backdrop-blur-xl">
      <div className="flex items-center gap-2 text-sm">
        <span className="text-ink-400">SentinelAI</span>
        <span className="text-ink-600">/</span>
        <span className="font-medium text-ink-100">{crumb}</span>
      </div>

      <div className="ml-auto flex items-center gap-3">
        <button
          onClick={() => setPaletteOpen(true)}
          className="group flex items-center gap-2 rounded-lg border border-white/[0.08] bg-white/[0.02] px-3 py-1.5 text-xs text-ink-400 transition-colors hover:border-white/15 hover:text-ink-200"
        >
          <Search size={13} />
          <span>Search…</span>
          <span className="ml-2 flex items-center gap-0.5 rounded border border-white/10 bg-white/[0.04] px-1 py-0.5 font-mono text-[0.62rem] text-ink-400">
            <Command size={9} />K
          </span>
        </button>

        <div className="flex items-center gap-2 rounded-lg border border-white/[0.08] bg-white/[0.02] py-1 pl-1 pr-2.5">
          <div className="flex h-6 w-6 items-center justify-center rounded-md bg-gradient-to-b from-white/20 to-white/[0.06] font-mono text-[0.62rem] font-semibold text-white">
            {initials}
          </div>
          <div className="hidden flex-col leading-none sm:flex">
            <span className="text-[0.7rem] font-medium text-ink-100">
              {user?.email?.split("@")[0] ?? "analyst"}
            </span>
            <span className="text-[0.6rem] uppercase tracking-wider text-ink-500">
              {user?.role ?? "tier2"}
            </span>
          </div>
        </div>
      </div>
    </header>
    </>
  );
}
