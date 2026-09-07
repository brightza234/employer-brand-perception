import type { SampleComment } from "@/lib/types";

const SENTIMENT_STYLE: Record<string, string> = {
  positive: "text-green-600 dark:text-green-400",
  neutral: "text-foreground/50",
  negative: "text-red-600 dark:text-red-400",
};

export default function SampleComments({ comments }: { comments: SampleComment[] }) {
  if (comments.length === 0) {
    return <p className="text-sm text-foreground/50">No sample comments for this theme yet.</p>;
  }

  return (
    <ul className="space-y-3">
      {comments.map((c, i) => (
        <li key={i} className="rounded border border-black/10 dark:border-white/10 p-3 text-sm">
          <p className="line-clamp-3">{c.text}</p>
          <div className="mt-2 flex items-center gap-2 text-xs text-foreground/50">
            <span className={SENTIMENT_STYLE[c.sentiment]}>{c.sentiment}</span>
            <span>·</span>
            <span>{c.source}</span>
            <span>·</span>
            <a href={c.url} target="_blank" rel="noreferrer" className="underline">
              source
            </a>
          </div>
        </li>
      ))}
    </ul>
  );
}
