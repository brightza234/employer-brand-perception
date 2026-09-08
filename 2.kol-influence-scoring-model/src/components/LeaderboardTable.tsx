import type { KolMetrics } from "@/lib/types";

function formatCompact(n: number): string {
  return new Intl.NumberFormat("en-US", { notation: "compact", maximumFractionDigits: 1 }).format(n);
}

export default function LeaderboardTable({ kols }: { kols: KolMetrics[] }) {
  return (
    <div className="overflow-x-auto rounded-lg border border-black/10 dark:border-white/10">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-black/10 text-left text-xs uppercase tracking-wide text-foreground/60 dark:border-white/10">
            <th className="px-4 py-3 font-medium">#</th>
            <th className="px-4 py-3 font-medium">KOL</th>
            <th className="px-4 py-3 text-right font-medium">Subscribers</th>
            <th className="px-4 py-3 text-right font-medium">Avg. views</th>
            <th className="px-4 py-3 text-right font-medium">Engagement rate</th>
            <th className="px-4 py-3 text-right font-medium">Upload frequency</th>
            <th className="px-4 py-3 text-right font-medium">Composite score</th>
          </tr>
        </thead>
        <tbody>
          {kols.map((k) => (
            <tr key={k.handle} className="border-b border-black/5 last:border-0 dark:border-white/5">
              <td className="px-4 py-3 tabular-nums text-foreground/60">{k.rank}</td>
              <td className="px-4 py-3 font-medium">{k.display_name}</td>
              <td className="px-4 py-3 text-right tabular-nums">{formatCompact(k.subscriber_count)}</td>
              <td className="px-4 py-3 text-right tabular-nums">{formatCompact(k.avg_views)}</td>
              <td className="px-4 py-3 text-right tabular-nums">{(k.engagement_rate * 100).toFixed(2)}%</td>
              <td className="px-4 py-3 text-right tabular-nums">{k.upload_frequency.toFixed(1)}/week</td>
              <td
                className="px-4 py-3 text-right tabular-nums font-semibold"
                style={{ color: k.composite_score >= 0 ? "var(--chart-positive)" : "var(--chart-negative)" }}
              >
                {k.composite_score >= 0 ? "+" : ""}
                {k.composite_score.toFixed(2)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
