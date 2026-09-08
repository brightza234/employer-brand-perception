export default function EmptyState() {
  return (
    <div className="mx-auto max-w-5xl px-6 py-16">
      <div className="rounded-lg border border-dashed border-black/15 dark:border-white/15 p-8 text-center">
        <h2 className="text-lg font-medium">No data yet</h2>
        <p className="mt-2 text-sm text-foreground/60">
          Run the collection and analysis pipeline first, then reload:
        </p>
        <pre className="mt-4 inline-block rounded bg-black/5 dark:bg-white/10 px-4 py-3 text-left text-sm">
          python scripts/collect_all.py{"\n"}python scripts/analyze.py
        </pre>
      </div>
    </div>
  );
}
