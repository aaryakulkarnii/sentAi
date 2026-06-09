"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion } from "framer-motion";
import {
  LayoutDashboard,
  AlertTriangle,
  Siren,
  Search,
  Shield,
  Brain,
  FileText,
  Settings,
  ShieldHalf,
  Server,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useAlertStore } from "@/stores/alerts";

const NAV = [
  { section: "Operations", items: [
    { href: "/dashboard", icon: LayoutDashboard, label: "Dashboard" },
    { href: "/alerts", icon: AlertTriangle, label: "Alerts" },
    { href: "/incidents", icon: Siren, label: "Incidents" },
    { href: "/assets", icon: Server, label: "Assets" },
  ]},
  { section: "Intelligence", items: [
    { href: "/investigate", icon: Brain, label: "AI Investigate" },
    { href: "/threat-intel", icon: Search, label: "Threat Intel" },
    { href: "/mitre", icon: Shield, label: "MITRE ATT&CK" },
  ]},
  { section: "Workspace", items: [
    { href: "/reports", icon: FileText, label: "Reports" },
    { href: "/settings", icon: Settings, label: "Settings" },
  ]},
];

export default function Sidebar() {
  const pathname = usePathname();
  const unread = useAlertStore((s) => s.unreadCount);

  return (
    <aside className="flex h-screen w-60 flex-shrink-0 flex-col border-r border-white/[0.06] bg-ink-900/80 backdrop-blur-xl">
      {/* Brand */}
      <div className="flex items-center gap-2.5 px-5 py-[1.15rem]">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg border border-white/10 bg-gradient-to-b from-white/[0.12] to-white/[0.02] shadow-[0_1px_0_0_rgba(255,255,255,0.1)_inset]">
          <ShieldHalf size={17} className="text-white" />
        </div>
        <div className="flex flex-col leading-none">
          <span className="text-[0.92rem] font-semibold tracking-tightest text-white">
            SentinelAI
          </span>
          <span className="mt-0.5 text-[0.62rem] font-medium uppercase tracking-[0.18em] text-ink-400">
            Autonomous SOC
          </span>
        </div>
      </div>

      <div className="mx-5 h-px bg-white/[0.06]" />

      {/* Nav */}
      <nav className="flex-1 overflow-y-auto px-3 py-4">
        {NAV.map((group) => (
          <div key={group.section} className="mb-5">
            <p className="px-3 pb-1.5 text-[0.62rem] font-semibold uppercase tracking-[0.16em] text-ink-500">
              {group.section}
            </p>
            <div className="space-y-0.5">
              {group.items.map(({ href, icon: Icon, label }) => {
                const active = pathname.startsWith(href);
                return (
                  <Link key={href} href={href} className="block">
                    <div
                      className={cn(
                        "group relative flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors",
                        active
                          ? "bg-white/[0.07] text-white"
                          : "text-ink-300 hover:bg-white/[0.04] hover:text-ink-100",
                      )}
                    >
                      {active && (
                        <motion.div
                          layoutId="nav-active"
                          className="absolute left-0 top-1/2 h-5 w-[2px] -translate-y-1/2 rounded-r-full bg-white"
                          transition={{ type: "spring", stiffness: 500, damping: 35 }}
                        />
                      )}
                      <Icon
                        size={16}
                        className={cn(
                          "transition-colors",
                          active ? "text-white" : "text-ink-400 group-hover:text-ink-200",
                        )}
                      />
                      <span className="font-medium">{label}</span>
                      {label === "Alerts" && unread > 0 && (
                        <span className="ml-auto rounded-full bg-sev-critical/15 px-1.5 py-0.5 font-mono text-[0.62rem] font-semibold text-sev-critical ring-1 ring-inset ring-sev-critical/30">
                          {unread}
                        </span>
                      )}
                    </div>
                  </Link>
                );
              })}
            </div>
          </div>
        ))}
      </nav>

      {/* System status */}
      <div className="m-3 rounded-lg border border-white/[0.06] bg-white/[0.02] px-3 py-2.5">
        <div className="flex items-center gap-2">
          <span className="relative flex h-2 w-2">
            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-sev-ok/60" />
            <span className="relative inline-flex h-2 w-2 rounded-full bg-sev-ok" />
          </span>
          <span className="text-xs font-medium text-ink-200">Systems nominal</span>
          <span className="ml-auto font-mono text-[0.62rem] text-ink-500">v0.1</span>
        </div>
      </div>
    </aside>
  );
}
