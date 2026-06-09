"use client";

import { useState } from "react";
import { Search, Loader2 } from "lucide-react";
import { threatIntelApi } from "@/lib/api";

export default function ThreatIntelCenter() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<object | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSearch = async () => {
    if (!query.trim()) return;
    setLoading(true);
    try {
      const { data } = await threatIntelApi.searchIoc(query);
      setResults(data);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="p-6 space-y-6">
      <h1 className="text-xl font-semibold text-white">Threat intelligence</h1>
      <div className="flex gap-3">
        <div className="relative flex-1">
          <Search size={14} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-500" />
          <input
            className="w-full bg-gray-900/60 border border-gray-800/50 rounded-xl pl-10 pr-4 py-2.5 text-sm text-white placeholder:text-gray-600 outline-none focus:ring-1 focus:ring-cyan-500/50"
            placeholder="Search IP, domain, hash…"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSearch()}
          />
        </div>
        <button
          onClick={handleSearch}
          disabled={loading}
          className="px-4 py-2.5 bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 text-white text-sm rounded-xl transition-colors font-medium"
        >
          {loading ? <Loader2 size={14} className="animate-spin" /> : "Search"}
        </button>
      </div>
      {results && (
        <pre className="bg-gray-900/60 border border-gray-800/50 rounded-xl p-5 text-xs font-mono text-gray-400 overflow-auto max-h-96">
          {JSON.stringify(results, null, 2)}
        </pre>
      )}
    </main>
  );
}
