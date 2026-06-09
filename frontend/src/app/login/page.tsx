"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { Zap, Loader2 } from "lucide-react";
import { authApi } from "@/lib/api";
import { useAuthStore } from "@/stores/auth";

export default function LoginPage() {
  const router = useRouter();
  const setAuth = useAuthStore((s) => s.setAuth);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
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
    <div className="min-h-screen flex items-center justify-center bg-gray-950 px-4">
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-sm"
      >
        <div className="flex items-center justify-center gap-2 mb-8">
          <Zap size={24} className="text-cyan-400" />
          <span className="text-xl font-semibold text-white tracking-tight">SentinelAI</span>
        </div>

        <form
          onSubmit={handleSubmit}
          className="bg-gray-900/60 border border-gray-800/50 rounded-xl p-6 space-y-4"
        >
          <h1 className="text-lg font-medium text-white">Sign in</h1>

          {error && (
            <p className="text-sm text-red-400 bg-red-500/10 border border-red-500/20 rounded-lg px-3 py-2">
              {error}
            </p>
          )}

          <div className="space-y-1.5">
            <label htmlFor="email" className="text-xs text-gray-500 uppercase tracking-wider">
              Email
            </label>
            <input
              id="email"
              type="email"
              required
              autoComplete="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full bg-gray-800/50 border border-gray-700/50 rounded-lg px-4 py-2.5 text-sm text-white outline-none focus:ring-1 focus:ring-cyan-500/50"
            />
          </div>

          <div className="space-y-1.5">
            <label htmlFor="password" className="text-xs text-gray-500 uppercase tracking-wider">
              Password
            </label>
            <input
              id="password"
              type="password"
              required
              autoComplete="current-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full bg-gray-800/50 border border-gray-700/50 rounded-lg px-4 py-2.5 text-sm text-white outline-none focus:ring-1 focus:ring-cyan-500/50"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full flex items-center justify-center gap-2 py-2.5 bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 text-white text-sm rounded-lg font-medium transition-colors"
          >
            {loading ? <Loader2 size={16} className="animate-spin" /> : null}
            Sign in
          </button>
        </form>
      </motion.div>
    </div>
  );
}
