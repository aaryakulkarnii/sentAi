"use client";

import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { mitreApi } from "@/lib/api";
import type { MitreTechnique } from "@/types";

export default function MitreMatrix() {
  const { data: techniques = [] } = useQuery<MitreTechnique[]>({
    queryKey: ["mitre-techniques"],
    queryFn: () => mitreApi.list().then((r) => r.data),
  });

  const byTactic = techniques.reduce<Record<string, MitreTechnique[]>>((acc, t) => {
    if (!acc[t.tactic]) acc[t.tactic] = [];
    acc[t.tactic].push(t);
    return acc;
  }, {});

  return (
    <main className="p-6 space-y-4">
      <h1 className="text-xl font-semibold text-white">MITRE ATT&amp;CK matrix</h1>
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
        {Object.entries(byTactic).map(([tactic, techs]) => (
          <motion.div
            key={tactic}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="bg-gray-900/60 border border-gray-800/50 rounded-xl overflow-hidden"
          >
            <div className="px-3 py-2 bg-purple-900/30 border-b border-purple-800/30">
              <p className="text-xs font-semibold text-purple-300 uppercase tracking-wider truncate">{tactic}</p>
            </div>
            <div className="divide-y divide-gray-800/20">
              {techs.map((t) => (
                <div key={t.id} className="px-3 py-2 hover:bg-gray-800/20 cursor-pointer transition-colors">
                  <p className="text-xs font-mono text-gray-500">{t.id}</p>
                  <p className="text-xs text-gray-300 truncate">{t.technique}</p>
                </div>
              ))}
            </div>
          </motion.div>
        ))}
        {techniques.length === 0 && (
          <p className="col-span-full text-center py-16 text-gray-600 text-sm">
            Load MITRE data with <code className="font-mono">python scripts/load_mitre.py</code>
          </p>
        )}
      </div>
    </main>
  );
}
