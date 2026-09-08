import EmptyState from "@/components/EmptyState";
import EngagementScatter from "@/components/EngagementScatter";
import LeaderboardTable from "@/components/LeaderboardTable";
import StatsPanel from "@/components/StatsPanel";
import { getScores } from "@/lib/data";

export default function Home() {
  const scores = getScores();
  if (!scores) return <EmptyState />;

  return (
    <div className="space-y-10">
      <section>
        <h1 className="text-2xl font-semibold tracking-tight">KOL Leaderboard</h1>
        <p className="mt-1 text-sm text-foreground/60">
          Ranked by composite score — a weighted blend of peer-relative engagement rate, average
          views, and upload consistency (z-scored within this {scores.kols.length}-channel niche, not
          raw subscriber count). Weights: {(scores.weights.engagement_rate * 100).toFixed(0)}%
          engagement, {(scores.weights.avg_views * 100).toFixed(0)}% views,{" "}
          {(scores.weights.upload_consistency * 100).toFixed(0)}% consistency.
        </p>
        <div className="mt-4">
          <LeaderboardTable kols={scores.kols} />
        </div>
      </section>

      <section>
        <h2 className="text-lg font-semibold tracking-tight">Size vs. engagement</h2>
        <p className="mt-1 text-sm text-foreground/60">
          Subscriber count (log scale) against engagement rate — dot color marks whether a KOL scores
          above or below the peer-group average.
        </p>
        <div className="mt-4">
          <EngagementScatter kols={scores.kols} />
        </div>
      </section>

      <section>
        <h2 className="text-lg font-semibold tracking-tight">Statistical validation</h2>
        <div className="mt-4">
          <StatsPanel
            correlations={scores.correlation_matrix}
            regression={scores.regression_engagement_on_size_and_consistency}
          />
        </div>
        <p className="mt-4 text-xs text-foreground/50">{scores.limitations}</p>
      </section>
    </div>
  );
}
