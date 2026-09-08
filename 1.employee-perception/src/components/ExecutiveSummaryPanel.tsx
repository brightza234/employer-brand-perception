"use client";

import { useState } from "react";

export default function ExecutiveSummaryPanel({ companies }: { companies: string[] }) {
  const [company, setCompany] = useState(companies[0]);
  const [summary, setSummary] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function generate() {
    setLoading(true);
    setError(null);
    setSummary(null);
    try {
      const res = await fetch("/api/summary", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ company }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error ?? "failed to generate summary");
      setSummary(data.summary);
    } catch (e) {
      setError(e instanceof Error ? e.message : "something went wrong");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="rounded-lg border border-black/10 dark:border-white/10 p-5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 className="font-medium">AI Executive Summary</h2>
        <div className="flex items-center gap-2">
          <select
            value={company}
            onChange={(e) => setCompany(e.target.value)}
            className="rounded border border-black/15 dark:border-white/15 bg-transparent px-2 py-1 text-sm"
          >
            {companies.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
          <button
            onClick={generate}
            disabled={loading}
            className="rounded bg-foreground text-background px-3 py-1 text-sm font-medium disabled:opacity-50"
          >
            {loading ? "Generating…" : "Generate"}
          </button>
        </div>
      </div>
      {error && <p className="mt-3 text-sm text-red-600 dark:text-red-400">{error}</p>}
      {summary && <p className="mt-3 text-sm leading-relaxed">{summary}</p>}
      {!summary && !error && !loading && (
        <p className="mt-3 text-sm text-foreground/50">Pick a company and click Generate.</p>
      )}
    </section>
  );
}
