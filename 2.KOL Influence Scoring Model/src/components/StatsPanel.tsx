import type { CorrelationPair, RegressionSummary } from "@/lib/types";

function StatTile({ label, value, sub }: { label: string; value: string; sub?: string }) {
  return (
    <div className="rounded-lg border border-black/10 p-4 dark:border-white/10">
      <div className="text-xs uppercase tracking-wide text-foreground/60">{label}</div>
      <div className="mt-1 text-2xl font-semibold">{value}</div>
      {sub && <div className="mt-1 text-xs text-foreground/50">{sub}</div>}
    </div>
  );
}

const LABELS: Record<string, string> = {
  subscriber_count__engagement_rate: "Subscribers ↔ Engagement rate",
  subscriber_count__upload_consistency: "Subscribers ↔ Upload consistency",
  engagement_rate__upload_consistency: "Engagement rate ↔ Upload consistency",
};

export default function StatsPanel({
  correlations,
  regression,
}: {
  correlations: Record<string, CorrelationPair>;
  regression: RegressionSummary;
}) {
  return (
    <div className="space-y-4">
      <div>
        <h3 className="mb-3 text-sm font-medium text-foreground/70">Pearson correlation (this peer group)</h3>
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
          {Object.entries(correlations).map(([key, { r, p_value }]) => (
            <StatTile
              key={key}
              label={LABELS[key] ?? key}
              value={r.toFixed(2)}
              sub={`p = ${p_value.toFixed(3)}${p_value < 0.05 ? " (significant at 0.05)" : ""}`}
            />
          ))}
        </div>
      </div>
      <div>
        <h3 className="mb-3 text-sm font-medium text-foreground/70">
          Regression: engagement_rate ~ subscriber_count + upload_consistency
        </h3>
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
          <StatTile
            label="R²"
            value={regression.r_squared.toFixed(3)}
            sub={`${(regression.r_squared * 100).toFixed(0)}% of engagement variance explained`}
          />
          <StatTile label="Coef. — subscriber_count" value={regression.coef_subscriber_count.toExponential(2)} />
          <StatTile label="Coef. — upload_consistency" value={regression.coef_upload_consistency.toFixed(4)} />
        </div>
        <p className="mt-2 text-xs text-foreground/50">n = {regression.n} channels</p>
      </div>
    </div>
  );
}
