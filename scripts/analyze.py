"""Classify collected comments (sentiment + HR theme) via Claude, then compute
aggregate stats per company and write data/processed_insights.json.

Usage:
    python scripts/analyze.py

Requires ANTHROPIC_API_KEY in .env.local, and data/raw_comments.json to exist
(run scripts/collect_all.py first).
"""

import collections
import datetime
import json
import os
import re
import sys

from anthropic import Anthropic
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(__file__))
from config import COMPANIES, SENTIMENTS, THEMES

RAW_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "raw_comments.json")
OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "processed_insights.json")
MODEL = "claude-haiku-4-5-20251001"
BATCH_SIZE = 10
SAMPLES_PER_THEME = 3

CLASSIFY_PROMPT = f"""You are labeling social media comments about companies as employers, for an
HR/employer-branding analysis. For each numbered comment below, classify:

- sentiment: one of {SENTIMENTS}
- theme: the single best-fit category from {THEMES}, or "Other" if none apply
- confidence: your confidence in the theme classification, 0.0-1.0

Respond with ONLY a JSON array (no markdown fences, no commentary), one object per
comment, in the same order, each shaped like:
{{"sentiment": "...", "theme": "...", "confidence": 0.0}}

Comments:
{{comments_block}}
"""


def load_raw_records() -> list[dict]:
    with open(RAW_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def strip_json_fences(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```(json)?", "", text).strip()
    text = re.sub(r"```$", "", text).strip()
    return text


def classify_batch(client: Anthropic, texts: list[str]) -> list[dict]:
    comments_block = "\n".join(f"{i + 1}. {t[:1000]}" for i, t in enumerate(texts))
    prompt = CLASSIFY_PROMPT.format(comments_block=comments_block)

    response = client.messages.create(
        model=MODEL,
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )
    raw_text = response.content[0].text
    parsed = json.loads(strip_json_fences(raw_text))

    if len(parsed) != len(texts):
        raise ValueError(f"expected {len(texts)} classifications, got {len(parsed)}")
    return parsed


def classify_all(client: Anthropic, records: list[dict]) -> list[dict]:
    classified = []
    for start in range(0, len(records), BATCH_SIZE):
        batch = records[start : start + BATCH_SIZE]
        print(f"[analyze] classifying {start + 1}-{start + len(batch)} of {len(records)}...")
        try:
            labels = classify_batch(client, [r["text"] for r in batch])
        except Exception as e:
            print(f"[analyze]   batch failed ({e}), skipping {len(batch)} records")
            continue
        for record, label in zip(batch, labels):
            classified.append({**record, **label})
    return classified


def month_bucket(iso_date: str) -> str:
    return iso_date[:7]  # "YYYY-MM"


def build_company_insights(company_name: str, records: list[dict]) -> dict:
    sentiment_counts = collections.Counter(r["sentiment"] for r in records)
    theme_counts = collections.Counter(r["theme"] for r in records)

    trend = collections.defaultdict(lambda: collections.Counter())
    for r in records:
        trend[month_bucket(r["date"])][r["sentiment"]] += 1
    trend_series = [
        {"period": period, **{s: trend[period].get(s, 0) for s in SENTIMENTS}}
        for period in sorted(trend.keys())
    ]

    samples_by_theme = collections.defaultdict(list)
    for r in records:
        theme = r["theme"]
        if len(samples_by_theme[theme]) < SAMPLES_PER_THEME:
            samples_by_theme[theme].append(
                {"text": r["text"][:500], "sentiment": r["sentiment"], "source": r["source"], "url": r["url"]}
            )

    return {
        "total_comments": len(records),
        "sentiment_distribution": {s: sentiment_counts.get(s, 0) for s in SENTIMENTS},
        "theme_distribution": {t: theme_counts.get(t, 0) for t in THEMES + ["Other"]},
        "trend": trend_series,
        "sample_comments": dict(samples_by_theme),
    }


def chi_square_theme_test(records: list[dict]) -> dict | None:
    """Chi-square test of independence: is theme distribution different across companies?"""
    try:
        from scipy.stats import chi2_contingency
    except ImportError:
        return None

    companies = sorted({r["company"] for r in records})
    themes = THEMES + ["Other"]
    full_table = [[sum(1 for r in records if r["company"] == c and r["theme"] == t) for t in themes] for c in companies]

    # drop theme columns nobody used, and require every company to have data
    used_columns = [i for i in range(len(themes)) if sum(row[i] for row in full_table) > 0]
    table = [[row[i] for i in used_columns] for row in full_table]

    if len(companies) < 2 or len(used_columns) < 2 or any(sum(row) == 0 for row in table):
        return None

    try:
        chi2, p_value, dof, _ = chi2_contingency(table)
    except ValueError:
        return None
    return {
        "chi2": round(float(chi2), 4),
        "p_value": round(float(p_value), 6),
        "degrees_of_freedom": int(dof),
        "significant_at_0.05": bool(p_value < 0.05),
        "note": "tests whether theme distribution differs significantly across companies",
    }


def main() -> None:
    load_dotenv(".env.local")
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    raw_records = load_raw_records()
    print(f"[analyze] {len(raw_records)} raw records loaded")

    classified = classify_all(client, raw_records)
    print(f"[analyze] {len(classified)} records classified")

    insights = {
        "generated_at": datetime.datetime.utcnow().isoformat() + "Z",
        "companies": {
            company["name"]: build_company_insights(
                company["name"], [r for r in classified if r["company"] == company["name"]]
            )
            for company in COMPANIES
        },
        "chi_square_theme_test": chi_square_theme_test(classified),
    }

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(insights, f, ensure_ascii=False, indent=2)
    print(f"[analyze] wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
