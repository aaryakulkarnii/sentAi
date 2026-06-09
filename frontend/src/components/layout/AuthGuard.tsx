"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Loader2 } from "lucide-react";
import { authApi } from "@/lib/api";
import { useAuthStore } from "@/stores/auth";
import { MOCK_AUTH, MOCK_TOKEN, MOCK_USER } from "@/lib/mockAuth";

export default function AuthGuard({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const { token, user, setAuth, clearAuth } = useAuthStore();
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    let cancelled = false;

    // Dev bypass: trust the local session, skip the backend /auth/me call.
    if (MOCK_AUTH) {
      const stored = localStorage.getItem("sentinel_token");
      if (!stored) {
        router.replace("/login");
        return;
      }
      setAuth(MOCK_USER, stored || MOCK_TOKEN);
      setChecking(false);
      return;
    }

    async function verify() {
      const stored = localStorage.getItem("sentinel_token");
      if (!stored) {
        router.replace("/login");
        return;
      }

      try {
        const { data } = await authApi.me();
        if (!cancelled) {
          setAuth(data, stored);
          setChecking(false);
        }
      } catch {
        if (!cancelled) {
          clearAuth();
          router.replace("/login");
        }
      }
    }

    if (token && user) {
      setChecking(false);
      return;
    }

    verify();
    return () => {
      cancelled = true;
    };
  }, [token, user, setAuth, clearAuth, router]);

  if (checking) {
    return (
      <div className="h-screen flex items-center justify-center bg-gray-950">
        <Loader2 className="animate-spin text-cyan-400" size={28} />
      </div>
    );
  }

  return <>{children}</>;
}
