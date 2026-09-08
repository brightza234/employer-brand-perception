import EmptyState from "@/components/EmptyState";
import Nav from "@/components/Nav";
import SampleComments from "@/components/SampleComments";
import ThemeBreakdownChart, { ThemeBreakdownRow } from "@/components/ThemeBreakdownChart";
import { getInsights } from "@/lib/data";

export default function ThemesPage() {
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
  const themes = Array.from(
    new Set(companies.flatMap((c) => Object.keys(insights.companies[c].theme_distribution)))
  );

  const rows: ThemeBreakdownRow[] = themes.map((theme) => {
    const row: ThemeBreakdownRow = { theme };
    for (const company of companies) {
      row[company] = insights.companies[company].theme_distribution[theme] ?? 0;
    }
    return row;
  });

  const chi = insights.chi_square_theme_test;

  return (
    <>
      <Nav />
      <main className="mx-auto max-w-5xl px-6 py-10 space-y-10">
        <div>
          <h1 className="text-xl font-semibold">Theme Breakdown</h1>
          <p className="mt-1 text-sm text-foreground/60">
            How often each HR theme comes up per company.
          </p>
        </div>

        <ThemeBreakdownChart data={rows} companies={companies} />

        {chi && (
          <div className="rounded-lg border border-black/10 dark:border-white/10 p-4 text-sm">
            <p className="font-medium">Chi-square test of independence</p>
            <p className="mt-1 text-foreground/60">
              χ² = {chi.chi2}, df = {chi.degrees_of_freedom}, p = {chi.p_value} —{" "}
              {chi["significant_at_0.05"]
                ? "theme distribution differs significantly between companies (p < 0.05)."
                : "no statistically significant difference in theme distribution (p ≥ 0.05)."}
            </p>
          </div>
        )}

        <div className="space-y-8">
          {themes.map((theme) => (
            <div key={theme}>
              <h2 className="font-medium">{theme}</h2>
              <div className="mt-3 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                {companies.map((company) => (
                  <div key={company}>
                    <p className="mb-2 text-xs font-medium text-foreground/60">{company}</p>
                    <SampleComments
                      comments={insights.companies[company].sample_comments[theme] ?? []}
                    />
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </main>
    </>
  );
}
