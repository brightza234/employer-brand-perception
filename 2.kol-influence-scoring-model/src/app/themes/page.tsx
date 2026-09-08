import EmptyState from "@/components/EmptyState";
import ThemeBreakdownChart from "@/components/ThemeBreakdownChart";
import { getContentThemes } from "@/lib/data";

export default function ThemesPage() {
  const themes = getContentThemes();
  if (!themes) return <EmptyState />;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Content Theme Breakdown</h1>
        <p className="mt-1 text-sm text-foreground/60">
          Each KOL&apos;s most recent videos classified by Claude into content themes, based on video
          titles.
        </p>
      </div>
      <ThemeBreakdownChart themes={themes} />
    </div>
  );
}
