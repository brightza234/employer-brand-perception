"""Collect news articles about target companies via NewsAPI.org.

Usage:
    python scripts/collect_news.py

Requires NEWSAPI_KEY in .env.local.
Note: NewsAPI free tier only returns articles from the last ~1 month.
"""

import datetime
import os
import sys

import requests
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(__file__))
from config import COMPANIES
from store import make_id, merge_new_records

NEWSAPI_URL = "https://newsapi.org/v2/everything"
PAGE_SIZE = 50


def collect_for_company(api_key: str, company: dict) -> list[dict]:
    records = []
    params = {
        "q": company["news_query"],
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": PAGE_SIZE,
        "apiKey": api_key,
    }
    response = requests.get(NEWSAPI_URL, params=params, timeout=30)
    response.raise_for_status()
    payload = response.json()

    for article in payload.get("articles", []):
        text = f"{article['title']}\n\n{article.get('description') or ''}".strip()
        if not text:
            continue
        records.append(
            {
                "id": make_id("news", article["url"], text),
                "source": "news",
                "company": company["name"],
                "text": text,
                "date": article["publishedAt"],
                "url": article["url"],
                "collected_at": datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z"),
            }
        )

    return records


def main() -> None:
    load_dotenv(".env.local")
    api_key = os.environ.get("NEWSAPI_KEY")
    if not api_key:
        print("[news] skipping — NEWSAPI_KEY not set in .env.local")
        return

    all_records = []
    for company in COMPANIES:
        print(f"[news] searching for {company['name']}...")
        company_records = collect_for_company(api_key, company)
        print(f"[news] {company['name']}: {len(company_records)} records")
        all_records.extend(company_records)

    added, total = merge_new_records(all_records)
    print(f"[news] done. added {added} new records, {total} total in data/raw_comments.json")


if __name__ == "__main__":
    main()
