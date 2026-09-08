import EmptyState from "@/components/EmptyState";
import Nav from "@/components/Nav";
import TrendChart, { TrendRow } from "@/components/TrendChart";
import { getInsights } from "@/lib/data";

export default function TrendPage() {
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
  const periods = Array.from(
    new Set(companies.flatMap((c) => insights.companies[c].trend.map((t) => t.period)))
  ).sort();

  const MIN_SAMPLE = 3; // quarters with fewer comments than this are too noisy to plot

  const rows: TrendRow[] = periods.map((period) => {
    const row: TrendRow = { period };
    for (const company of companies) {
      const point = insights.companies[company].trend.find((t) => t.period === period);
      const total = point ? point.positive + point.neutral + point.negative : 0;
      row[company] = point && total >= MIN_SAMPLE ? (point.positive - point.negative) / total : null;
    }
    return row;
  });

  return (
    <>
      <Nav />
      <main className="mx-auto max-w-5xl px-6 py-10 space-y-6">
        <div>
          <h1 className="text-xl font-semibold">Sentiment Trend</h1>
          <p className="mt-1 text-sm text-foreground/60">
            Net sentiment score per quarter: (positive − negative) / total, ranging from −1 to 1.
            Quarters with fewer than {MIN_SAMPLE} comments are left as gaps rather than plotted.
          </p>
        </div>

        <TrendChart data={rows} companies={companies} />
      </main>
    </>
  );
}
