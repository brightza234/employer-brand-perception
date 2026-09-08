# KOL Influence & Engagement Scoring Model

A statistical ranking model for YouTube KOLs (key opinion leaders) in the Thai tech/gadget-review
niche — scored on peer-relative engagement and consistency, not raw subscriber count.

## What this project demonstrates

Follower count is the metric brands default to, and it's the wrong one: a channel with 2M
subscribers and a 1% engagement rate is arguably less "influential" per view than a 70K-subscriber
channel whose audience actually reacts. This project is built to show the statistical work that
separates the two, not just a follower leaderboard with a chart on top.

- **Normalization across mismatched units.** `subscriber_count` lives in the hundred-thousands to
  millions; `engagement_rate` lives in 0.01–0.1. Combining them directly would let subscriber count
  dominate any composite score. Every metric is **z-scored relative to the curated peer group**
  (`z(x) = (x - mean(x)) / std(x)`) before being combined — see
  [`scripts/compute_scores.py`](scripts/compute_scores.py) for the full derivation.
- **A justified, documented weighting.** `composite_score = 0.4·z(engagement_rate) +
  0.3·z(avg_views) + 0.3·z(upload_consistency)`. Engagement gets the largest weight because it's
  the metric least correlated with channel size — see below — and therefore the one that actually
  distinguishes "influential" from "big."
- **Statistical validation, not just a score.** A Pearson correlation matrix checks whether bigger
  channels really do have lower engagement in this niche, and a multiple linear regression reports
  how much of engagement-rate variance subscriber count and posting consistency jointly explain
  (R²) — both computed fresh on every run, both reported with their limitations, not cherry-picked.
- **Honest about sample size.** 15 curated channels in one niche is enough to see a real pattern in
  *this* peer group, not enough to generalize to "Thai YouTube" — the dashboard says so directly
  rather than implying more confidence than the data supports.

## What it found

_To be filled in after the first live data collection run — see "Running it locally" below.
`data/kol_scores.json` (committed) holds whatever the last run produced; this section will
summarize the leaderboard result and the correlation/regression findings once real API keys are
in place._

## Pipeline

```
data/kol_list.json (curated 15 Thai tech-review channels)
          │
          ▼
scripts/collect_youtube.py   ──→  data/raw_kol_stats.json   (channel + last-15-video stats)
          │                              │
          │                              ├──→ scripts/compute_scores.py ──→ data/kol_scores.json
          │                              │      (z-scores, composite score, correlation, regression)
          │                              │
          │                              └──→ scripts/classify_themes.py ──→ data/content_themes.json
          │                                     (Claude: content theme per video)
          ▼
     Next.js dashboard (reads the two output JSON files above)
```

1. **Curate** — 15 real, active Thai tech/gadget-review YouTube channels spanning ~9.5K to 2.5M
   subscribers (`data/kol_list.json`), picked for size diversity so z-scoring has a meaningful
   distribution to work against.
2. **Collect** (`collect_youtube.py`) — for each channel: current subscriber count and the most
   recent 15 videos' view/like/comment counts and publish dates, via the YouTube Data API v3.
3. **Score** (`compute_scores.py`) — derives `engagement_rate` and `upload_consistency` per
   channel, z-scores every metric within the peer group, computes the weighted composite score and
   rank, then validates the metrics with a Pearson correlation matrix and an OLS regression.
4. **Classify** (`classify_themes.py`) — sends each channel's video titles to Claude
   (`claude-haiku-4-5`) to bucket them into content themes (Smartphone, Laptop/PC, Wearable/Gadget,
   Home Appliance/Audio, Tech News/Update, Other/Lifestyle).
5. **Visualize** — a Next.js dashboard: a ranked leaderboard table, a subscriber-vs-engagement
   scatter plot (log-scaled x-axis, colored by above/below-average composite score), a statistical
   validation panel, and a per-KOL content theme breakdown.

## Tech stack

- **Collection**: Python, `google-api-python-client` (YouTube Data API v3)
- **Analysis**: `numpy` + `scipy.stats` for z-scores, Pearson correlation, and OLS regression;
  Claude (`claude-haiku-4-5`) for content theme classification
- **Dashboard**: Next.js (App Router) + TypeScript + Tailwind CSS + Recharts
- **Deployment**: GitHub → Vercel

## Running it locally

```bash
npm install
pip install -r requirements.txt
cp .env.example .env.local   # fill in your API keys
python scripts/collect_youtube.py
python scripts/compute_scores.py
python scripts/classify_themes.py
npm run dev
```

Get API keys from the [Google Cloud Console](https://console.cloud.google.com) (YouTube Data API
v3) and the [Anthropic Console](https://console.anthropic.com).

## Limitations (and why they're here on purpose)

- **Sample size is 15 channels, one niche.** Correlation and regression results describe *this*
  curated peer group, not Thai YouTube in general — a p-value here is a directional signal, not
  proof, and the dashboard states this rather than implying more statistical confidence than 15
  data points can support.
- **Metrics are a snapshot.** `avg_views`, `engagement_rate`, and `upload_consistency` are derived
  from each channel's most recent 15 uploads at collection time — one viral hit or one unusually
  quiet week can move a channel's numbers and rank noticeably. Re-running the collector weekly
  (`data/score_history.json`, appended by `compute_scores.py` on every run) is what would let a
  future iteration classify channels as Rising/Stable/Declining instead of reading one snapshot as
  the whole picture.
- **Content theme classification runs on titles, not full video content** — an LLM judging a title
  alone will occasionally miscategorize a video whose actual content diverges from its title
  (clickbait, or a title in a different language than the video).
