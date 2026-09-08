"""Turn raw YouTube stats into a normalized, statistically-validated KOL score.

Pipeline:
  1. Derive per-KOL metrics from the last VIDEOS_PER_KOL uploads:
       avg_views, avg_likes, avg_comments, engagement_rate, upload_consistency
  2. Z-score each metric *relative to this peer group* (not an absolute scale) —
     subscriber_count lives in the hundred-thousands/millions while engagement_rate
     lives in 0.01-0.1, so combining raw values would let subscriber_count dominate.
     z(x) = (x - mean(x)) / std(x), std computed with ddof=0 (population std) since
     the curated 15-25 KOLs *are* the full peer group we're scoring, not a sample
     drawn from a larger population.
  3. Composite score = weighted sum of z-scores (weights in config.py).
  4. Validate the metrics statistically: Pearson correlation matrix between
     subscriber_count, engagement_rate, upload_consistency, plus a multiple linear
     regression predicting engagement_rate from the other two (reports R²).

Usage:
    python scripts/compute_scores.py
"""

import datetime
import json
import os
import sys

import numpy as np
from scipy import stats

sys.path.insert(0, os.path.dirname(__file__))
from config import (
    RAW_STATS_PATH,
    SCORES_PATH,
    UPLOAD_CONSISTENCY_WINDOW_DAYS,
    WEIGHT_AVG_VIEWS,
    WEIGHT_ENGAGEMENT_RATE,
    WEIGHT_UPLOAD_CONSISTENCY,
)

HISTORY_PATH = os.path.join(os.path.dirname(RAW_STATS_PATH), "score_history.json")


def derive_metrics(kol: dict, collected_at: datetime.datetime) -> dict:
    """Compute the four raw (pre-normalization) metrics for one KOL.

    engagement_rate = (avg_likes + avg_comments) / avg_views — the share of viewers
    who bothered to react, independent of how many people merely saw the video.

    upload_consistency = number of the fetched videos published within the last
    UPLOAD_CONSISTENCY_WINDOW_DAYS — a proxy for "is this creator still active",
    not a measure of quality.
    """
    videos = kol["videos"]
    n = len(videos)
    avg_views = sum(v["view_count"] for v in videos) / n if n else 0.0
    avg_likes = sum(v["like_count"] for v in videos) / n if n else 0.0
    avg_comments = sum(v["comment_count"] for v in videos) / n if n else 0.0
    engagement_rate = (avg_likes + avg_comments) / avg_views if avg_views else 0.0

    cutoff = collected_at - datetime.timedelta(days=UPLOAD_CONSISTENCY_WINDOW_DAYS)
    upload_consistency = sum(
        1 for v in videos if datetime.datetime.fromisoformat(v["published_at"].replace("Z", "+00:00")) >= cutoff
    )

    return {
        "handle": kol["handle"],
        "display_name": kol["display_name"],
        "subscriber_count": kol["subscriber_count"],
        "video_sample_size": n,
        "avg_views": avg_views,
        "avg_likes": avg_likes,
        "avg_comments": avg_comments,
        "engagement_rate": engagement_rate,
        "upload_consistency": upload_consistency,
    }


def zscore(values: list[float]) -> np.ndarray:
    arr = np.array(values, dtype=float)
    std = arr.std(ddof=0)
    if std == 0:
        return np.zeros_like(arr)
    return (arr - arr.mean()) / std


def add_composite_scores(metrics: list[dict]) -> None:
    z_engagement = zscore([m["engagement_rate"] for m in metrics])
    z_views = zscore([m["avg_views"] for m in metrics])
    z_consistency = zscore([m["upload_consistency"] for m in metrics])

    for i, m in enumerate(metrics):
        m["z_engagement_rate"] = float(z_engagement[i])
        m["z_avg_views"] = float(z_views[i])
        m["z_upload_consistency"] = float(z_consistency[i])
        m["composite_score"] = float(
            WEIGHT_ENGAGEMENT_RATE * z_engagement[i]
            + WEIGHT_AVG_VIEWS * z_views[i]
            + WEIGHT_UPLOAD_CONSISTENCY * z_consistency[i]
        )

    metrics.sort(key=lambda m: m["composite_score"], reverse=True)
    for rank, m in enumerate(metrics, start=1):
        m["rank"] = rank


def correlation_matrix(metrics: list[dict]) -> dict:
    """Pearson r + two-tailed p-value for every pair of the three raw metrics.

    With only 15-25 KOLs, p-values here should be read as directional, not as
    proof — see the `limitations` note in the output file.
    """
    fields = ["subscriber_count", "engagement_rate", "upload_consistency"]
    series = {f: np.array([m[f] for m in metrics], dtype=float) for f in fields}
    result = {}
    for i, a in enumerate(fields):
        for b in fields[i + 1 :]:
            r, p = stats.pearsonr(series[a], series[b])
            result[f"{a}__{b}"] = {"r": float(r), "p_value": float(p)}
    return result


def regression_engagement_on_size_and_consistency(metrics: list[dict]) -> dict:
    """OLS: engagement_rate ~ subscriber_count + upload_consistency.

    Solved via least squares on the design matrix [1, subscriber_count,
    upload_consistency] rather than pulling in a modeling library — with ~15-25
    rows and 2 predictors this is a fully-determined small linear system.
    Reports R² = 1 - SS_res/SS_tot, i.e. the fraction of variance in
    engagement_rate explained by channel size and posting consistency.
    """
    y = np.array([m["engagement_rate"] for m in metrics], dtype=float)
    x1 = np.array([m["subscriber_count"] for m in metrics], dtype=float)
    x2 = np.array([m["upload_consistency"] for m in metrics], dtype=float)
    X = np.column_stack([np.ones_like(y), x1, x2])

    coeffs, _, _, _ = np.linalg.lstsq(X, y, rcond=None)
    y_pred = X @ coeffs
    ss_res = float(np.sum((y - y_pred) ** 2))
    ss_tot = float(np.sum((y - y.mean()) ** 2))
    r_squared = 1 - ss_res / ss_tot if ss_tot else 0.0

    return {
        "intercept": float(coeffs[0]),
        "coef_subscriber_count": float(coeffs[1]),
        "coef_upload_consistency": float(coeffs[2]),
        "r_squared": float(r_squared),
        "n": len(metrics),
    }


def append_history(metrics: list[dict], collected_at: str) -> None:
    """Append this run's composite scores to a running history file so that,
    once the collector has run more than once, Phase 5 trend classification
    (Rising/Stable/Declining) has something to compute a % change against."""
    history = []
    if os.path.exists(HISTORY_PATH):
        with open(HISTORY_PATH, encoding="utf-8") as f:
            history = json.load(f)
    history.append(
        {
            "collected_at": collected_at,
            "scores": [{"handle": m["handle"], "composite_score": m["composite_score"]} for m in metrics],
        }
    )
    with open(HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def main() -> None:
    with open(RAW_STATS_PATH, encoding="utf-8") as f:
        snapshot = json.load(f)

    collected_at = datetime.datetime.fromisoformat(snapshot["collected_at"].replace("Z", "+00:00"))
    metrics = [derive_metrics(kol, collected_at) for kol in snapshot["kols"]]

    add_composite_scores(metrics)
    correlations = correlation_matrix(metrics)
    regression = regression_engagement_on_size_and_consistency(metrics)
    append_history(metrics, snapshot["collected_at"])

    output = {
        "collected_at": snapshot["collected_at"],
        "computed_at": datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z"),
        "weights": {
            "engagement_rate": WEIGHT_ENGAGEMENT_RATE,
            "avg_views": WEIGHT_AVG_VIEWS,
            "upload_consistency": WEIGHT_UPLOAD_CONSISTENCY,
        },
        "kols": metrics,
        "correlation_matrix": correlations,
        "regression_engagement_on_size_and_consistency": regression,
        "limitations": (
            f"Sample size is {len(metrics)} channels — a single curated niche, not a random "
            "sample of Thai tech KOLs. Correlation and regression results here are directional "
            "signals for this specific peer group, not generalizable population estimates. "
            "Metrics are derived from each channel's most recent uploads at collection time, "
            "so a single viral or unusually quiet video can shift a KOL's numbers noticeably."
        ),
    }

    os.makedirs(os.path.dirname(SCORES_PATH), exist_ok=True)
    with open(SCORES_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"[scores] wrote {len(metrics)} KOL scores to {SCORES_PATH}")
    print(f"[scores] engagement_rate ~ subscriber_count + upload_consistency: R² = {regression['r_squared']:.3f}")


if __name__ == "__main__":
    main()
