"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion } from "framer-motion";
import {
  LayoutDashboard, AlertTriangle, Siren, Search,
  Shield, Brain, FileText, Settings, Zap,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useAlertStore } from "@/stores/alerts";

const NAV = [
  { href: "/dashboard",    icon: LayoutDashboard, label: "Dashboard"        },
  { href: "/alerts",       icon: AlertTriangle,   label: "Alerts"           },
  { href: "/incidents",    icon: Siren,           label: "Incidents"        },
  { href: "/investigate",  icon: Brain,           label: "AI Investigate"   },
  { href: "/threat-intel", icon: Search,          label: "Threat Intel"     },
  { href: "/mitre",        icon: Shield,          label: "MITRE ATT&CK"     },
  { href: "/reports",      icon: FileText,        label: "Reports"          },
  { href: "/settings",     icon: Settings,        label: "Settings"         },
];

export default function Sidebar() {
  const pathname = usePathname();
  const unread = useAlertStore((s) => s.unreadCount);

  return (
    <aside className="w-56 flex-shrink-0 bg-gray-900/60 border-r border-gray-800/50 flex flex-col h-screen">
      {/* Logo */}
      <div className="px-5 py-4 border-b border-gray-800/50 flex items-center gap-2">
        <Zap size={20} className="text-cyan-400" />
        <span className="font-semibold tracking-tight text-sm text-white">SentinelAI</span>
        <span className="ml-auto text-[10px] font-mono text-gray-500 bg-gray-800 px-1.5 py-0.5 rounded">
          v0.1
        </span>
      </div>

      {/* Nav */}
      <nav className="flex-1 py-4 space-y-0.5 px-2">
        {NAV.map(({ href, icon: Icon, label }) => {
          const active = pathname.startsWith(href);
          return (
            <Link key={href} href={href}>
              <motion.div
                whileHover={{ x: 2 }}
                className={cn(
                  "flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors relative",
                  active
                    ? "bg-cyan-500/10 text-cyan-300 font-medium"
                    : "text-gray-400 hover:text-gray-200 hover:bg-gray-800/50"
                )}
              >
                <Icon size={16} />
                <span>{label}</span>
                {label === "Alerts" && unread > 0 && (
                  <span className="ml-auto bg-red-500 text-white text-[10px] font-mono px-1.5 py-0.5 rounded-full">
                    {unread}
                  </span>
                )}
                {active && (
                  <motion.div
                    layoutId="sidebar-indicator"
                    className="absolute left-0 top-1/2 -translate-y-1/2 w-0.5 h-4 bg-cyan-400 rounded-r"
                  />
                )}
              </motion.div>
            </Link>
          );
        })}
      </nav>

      {/* Status bar */}
      <div className="px-4 py-3 border-t border-gray-800/50 text-[11px] font-mono text-gray-500 flex items-center gap-2">
        <span className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse-slow" />
        Systems nominal
      </div>
    </aside>
  );
}
