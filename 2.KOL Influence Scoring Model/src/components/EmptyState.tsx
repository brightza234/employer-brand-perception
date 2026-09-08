export default function EmptyState() {
  return (
    <div className="rounded-lg border border-dashed border-black/15 p-8 text-center dark:border-white/15">
      <h2 className="text-lg font-medium">No data yet</h2>
      <p className="mt-2 text-sm text-foreground/60">Run the collection and analysis pipeline first, then reload:</p>
      <pre className="mt-4 inline-block rounded bg-black/5 px-4 py-3 text-left text-sm dark:bg-white/10">
        python scripts/collect_youtube.py{"\n"}python scripts/compute_scores.py{"\n"}python scripts/classify_themes.py
      </pre>
    </div>
  );
}
