"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Brain, Play, Loader2 } from "lucide-react";
import { investigationsApi } from "@/lib/api";
import type { Investigation } from "@/types";

export default function AIConsole() {
  const [incidentId, setIncidentId] = useState("");
  const [investigation, setInvestigation] = useState<Investigation | null>(null);
  const [loading, setLoading] = useState(false);

  const handleTrigger = async () => {
    if (!incidentId.trim()) return;
    setLoading(true);
    try {
      await investigationsApi.trigger(incidentId);
      // Poll for result
      await new Promise((res) => setTimeout(res, 3000));
      const { data } = await investigationsApi.get(incidentId);
      setInvestigation(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="p-6 space-y-6">
      <div className="flex items-center gap-3">
        <Brain size={20} className="text-purple-400" />
        <h1 className="text-xl font-semibold text-white">AI investigation console</h1>
      </div>

      {/* Trigger */}
      <div className="bg-gray-900/60 border border-gray-800/50 rounded-xl p-5 flex gap-3">
        <input
          className="flex-1 bg-gray-800/50 border border-gray-700/50 rounded-lg px-4 py-2.5 text-sm text-white placeholder:text-gray-600 outline-none focus:ring-1 focus:ring-purple-500/50"
          placeholder="Incident ID…"
          value={incidentId}
          onChange={(e) => setIncidentId(e.target.value)}
        />
        <button
          onClick={handleTrigger}
          disabled={loading || !incidentId}
          className="flex items-center gap-2 px-4 py-2.5 bg-purple-600 hover:bg-purple-500 disabled:opacity-50 text-white text-sm rounded-lg transition-colors font-medium"
        >
          {loading ? <Loader2 size={14} className="animate-spin" /> : <Play size={14} />}
          Investigate
        </button>
      </div>

      {/* Result */}
      <AnimatePresence>
        {investigation && (
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-gray-900/60 border border-purple-500/20 rounded-xl p-5 space-y-4"
          >
            <div className="flex items-center justify-between">
              <h2 className="font-medium text-white">Investigation result</h2>
              <span className="font-mono text-sm text-purple-400">Risk: {investigation.risk_score}</span>
            </div>
            <pre className="bg-gray-950/50 rounded-lg p-4 text-xs font-mono text-gray-400 overflow-auto max-h-96">
              {JSON.stringify(investigation, null, 2)}
            </pre>
          </motion.div>
        )}
      </AnimatePresence>
    </main>
  );
}
