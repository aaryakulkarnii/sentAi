"use client";

import { useAuthStore } from "@/stores/auth";
import { useRouter } from "next/navigation";

export default function SettingsPage() {
  const { user, clearAuth } = useAuthStore();
  const router = useRouter();

  const handleLogout = () => {
    clearAuth();
    router.replace("/login");
  };

  return (
    <main className="p-6 space-y-6">
      <h1 className="text-xl font-semibold text-white">Settings</h1>

      <div className="bg-gray-900/60 border border-gray-800/50 rounded-xl p-5 space-y-3 max-w-md">
        <h2 className="text-sm font-medium text-gray-400 uppercase tracking-wider">Account</h2>
        {user && (
          <>
            <p className="text-sm text-white">{user.email}</p>
            <p className="text-xs font-mono text-gray-500">Role: {user.role}</p>
          </>
        )}
        <button
          onClick={handleLogout}
          className="mt-2 px-4 py-2 text-sm text-red-400 border border-red-500/30 rounded-lg hover:bg-red-500/10 transition-colors"
        >
          Sign out
        </button>
      </div>
    </main>
  );
}
