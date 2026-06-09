"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { ShieldHalf, Loader2, ArrowRight } from "lucide-react";
import { authApi } from "@/lib/api";
import { useAuthStore } from "@/stores/auth";
import { MOCK_AUTH, MOCK_TOKEN, MOCK_USER } from "@/lib/mockAuth";

export default function LoginPage() {
  const router = useRouter();
  const setAuth = useAuthStore((s) => s.setAuth);
  const [email, setEmail] = useState(MOCK_AUTH ? MOCK_USER.email : "");
  const [password, setPassword] = useState(MOCK_AUTH ? "password" : "");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    if (MOCK_AUTH) {
      setAuth(MOCK_USER, MOCK_TOKEN);
      router.replace("/dashboard");
      return;
    }

    try {
      const { data } = await authApi.login(email, password);
      setAuth(data.user, data.access_token);
      router.replace("/dashboard");
    } catch {
      setError("Invalid email or password");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative flex min-h-screen items-center justify-center px-4">
      <div className="dot-grid pointer-events-none absolute inset-0 opacity-40 [mask-image:radial-gradient(60%_50%_at_50%_40%,black,transparent)]" />

      <motion.div
        initial={{ opacity: 0, y: 14 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
        className="relative w-full max-w-[22rem]"
      >
        <div className="mb-8 flex flex-col items-center gap-3">
          <div className="flex h-12 w-12 items-center justify-center rounded-2xl border border-white/10 bg-gradient-to-b from-white/[0.14] to-white/[0.02] shadow-glow">
            <ShieldHalf size={24} className="text-white" />
          </div>
          <div className="text-center">
            <h1 className="text-lg font-semibold tracking-tightest text-white">SentinelAI</h1>
            <p className="mt-0.5 text-xs text-ink-400">Autonomous Security Operations</p>
          </div>
        </div>

        <div className="panel p-6">
          <form onSubmit={handleSubmit} className="relative space-y-4">
            <div>
              <h2 className="text-sm font-medium text-white">Sign in to your workspace</h2>
              <p className="mt-0.5 text-xs text-ink-400">Enter your credentials to continue</p>
            </div>

            {error && (
              <p className="rounded-lg border border-sev-critical/20 bg-sev-critical/10 px-3 py-2 text-sm text-sev-critical">
                {error}
              </p>
            )}

            <div className="space-y-1.5">
              <label htmlFor="email" className="text-[0.7rem] font-medium uppercase tracking-wider text-ink-400">
                Email
              </label>
              <input
                id="email"
                type="email"
                required
                autoComplete="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full rounded-lg border border-white/10 bg-white/[0.03] px-3.5 py-2.5 text-sm text-white outline-none transition-colors focus:border-white/25 focus:bg-white/[0.05]"
              />
            </div>

            <div className="space-y-1.5">
              <label htmlFor="password" className="text-[0.7rem] font-medium uppercase tracking-wider text-ink-400">
                Password
              </label>
              <input
                id="password"
                type="password"
                required
                autoComplete="current-password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full rounded-lg border border-white/10 bg-white/[0.03] px-3.5 py-2.5 text-sm text-white outline-none transition-colors focus:border-white/25 focus:bg-white/[0.05]"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="group flex w-full items-center justify-center gap-2 rounded-lg bg-white py-2.5 text-sm font-medium text-ink-950 transition-all hover:bg-ink-100 disabled:opacity-50"
            >
              {loading ? (
                <Loader2 size={15} className="animate-spin" />
              ) : (
                <>
                  Sign in
                  <ArrowRight size={14} className="transition-transform group-hover:translate-x-0.5" />
                </>
              )}
            </button>
          </form>
        </div>

        {MOCK_AUTH && (
          <p className="mt-4 text-center text-[0.7rem] text-ink-500">
            Demo mode · any credentials work
          </p>
        )}
      </motion.div>
    </div>
  );
}
