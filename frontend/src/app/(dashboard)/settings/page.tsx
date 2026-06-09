"use client";

import { useRouter } from "next/navigation";
import { Settings as SettingsIcon, User, LogOut, KeyRound } from "lucide-react";
import { useAuthStore } from "@/stores/auth";
import { PageHeader, Panel, Button } from "@/components/ui";

export default function SettingsPage() {
  const { user, clearAuth } = useAuthStore();
  const router = useRouter();

  const handleLogout = () => {
    clearAuth();
    router.replace("/login");
  };

  return (
    <main className="mx-auto max-w-[800px] space-y-6 p-6">
      <PageHeader title="Settings" subtitle="Manage your account and workspace" icon={<SettingsIcon size={17} />} />

      <Panel className="p-5">
        <div className="mb-4 flex items-center gap-2 text-sm font-medium text-white">
          <User size={15} className="text-ink-400" />
          Account
        </div>
        <div className="flex items-center gap-4">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-b from-white/20 to-white/[0.06] font-mono text-sm font-semibold text-white">
            {user?.email?.slice(0, 2).toUpperCase() ?? "AN"}
          </div>
          <div className="flex-1">
            <p className="text-sm text-white">{user?.email ?? "—"}</p>
            <p className="mt-0.5 text-xs uppercase tracking-wider text-ink-400">
              {user?.role ?? "tier2"} analyst
            </p>
          </div>
          <Button variant="danger" size="sm" onClick={handleLogout}>
            <LogOut size={13} />
            Sign out
          </Button>
        </div>
      </Panel>

      <Panel className="p-5">
        <div className="mb-1 flex items-center gap-2 text-sm font-medium text-white">
          <KeyRound size={15} className="text-ink-400" />
          API keys & detection rules
        </div>
        <p className="text-xs text-ink-400">
          API key management, detection-rule administration, and user management arrive in Phase 4.
        </p>
      </Panel>
    </main>
  );
}
