import CompanySentimentChart, { CompanySentimentRow } from "@/components/CompanySentimentChart";
import EmptyState from "@/components/EmptyState";
import ExecutiveSummaryPanel from "@/components/ExecutiveSummaryPanel";
import Nav from "@/components/Nav";
import { getInsights } from "@/lib/data";

export default function OverviewPage() {
  const insights = getInsights();

  if (!insights) {
    return (
      <>
        <Nav />
        <EmptyState />
      </>
    );
  }

  const companies = Object.keys(insights.companies);
  const sentimentRows: CompanySentimentRow[] = companies.map((company) => ({
    company,
    ...insights.companies[company].sentiment_distribution,
  }));

  return (
    <>
      <Nav />
      <main className="mx-auto max-w-5xl px-6 py-10 space-y-10">
        <div>
          <h1 className="text-xl font-semibold">Overview</h1>
          <p className="mt-1 text-sm text-foreground/60">
            Sentiment distribution per company, aggregated from Reddit, YouTube and news mentions.
          </p>
        </div>

        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3">
          {companies.map((company) => (
            <div key={company} className="rounded-lg border border-black/10 dark:border-white/10 p-4">
              <p className="text-sm text-foreground/60">{company}</p>
              <p className="mt-1 text-2xl font-semibold">
                {insights.companies[company].total_comments}
              </p>
              <p className="text-xs text-foreground/50">comments analyzed</p>
            </div>
          ))}
        </div>

        <CompanySentimentChart data={sentimentRows} />

        <ExecutiveSummaryPanel companies={companies} />
      </main>
    </>
  );
}
