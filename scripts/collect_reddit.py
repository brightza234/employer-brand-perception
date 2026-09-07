"""Collect Reddit posts + comments mentioning target companies.

Usage:
    python scripts/collect_reddit.py

Requires REDDIT_CLIENT_ID / REDDIT_CLIENT_SECRET in .env.local.
"""

import datetime
import os
import sys

import praw
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(__file__))
from config import COMPANIES
from store import make_id, merge_new_records

SEARCH_LIMIT = 50
COMMENTS_PER_SUBMISSION = 20


def get_reddit_client() -> praw.Reddit:
    client_id = os.environ["REDDIT_CLIENT_ID"]
    client_secret = os.environ["REDDIT_CLIENT_SECRET"]
    return praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent="employer-brand-perception/0.1 (by u/anonymous)",
    )


def collect_for_company(reddit: praw.Reddit, company: dict) -> list[dict]:
    records = []
    subreddit_names = "+".join(company["reddit_subreddits"])
    subreddit = reddit.subreddit(subreddit_names)

    for submission in subreddit.search(company["reddit_query"], limit=SEARCH_LIMIT, sort="relevance"):
        text = f"{submission.title}\n\n{submission.selftext}".strip()
        if text:
            records.append(
                {
                    "id": make_id("reddit", submission.url, text),
                    "source": "reddit",
                    "company": company["name"],
                    "text": text,
                    "date": datetime.datetime.utcfromtimestamp(submission.created_utc).isoformat() + "Z",
                    "url": f"https://reddit.com{submission.permalink}",
                    "collected_at": datetime.datetime.utcnow().isoformat() + "Z",
                }
            )

        submission.comments.replace_more(limit=0)
        for comment in submission.comments.list()[:COMMENTS_PER_SUBMISSION]:
            body = getattr(comment, "body", "").strip()
            if not body or body in ("[deleted]", "[removed]"):
                continue
            records.append(
                {
                    "id": make_id("reddit", f"{submission.url}#{comment.id}", body),
                    "source": "reddit",
                    "company": company["name"],
                    "text": body,
                    "date": datetime.datetime.utcfromtimestamp(comment.created_utc).isoformat() + "Z",
                    "url": f"https://reddit.com{submission.permalink}{comment.id}/",
                    "collected_at": datetime.datetime.utcnow().isoformat() + "Z",
                }
            )

    return records


def main() -> None:
    load_dotenv(".env.local")
    reddit = get_reddit_client()

    all_records = []
    for company in COMPANIES:
        print(f"[reddit] searching for {company['name']}...")
        company_records = collect_for_company(reddit, company)
        print(f"[reddit] {company['name']}: {len(company_records)} records")
        all_records.extend(company_records)

    added, total = merge_new_records(all_records)
    print(f"[reddit] done. added {added} new records, {total} total in data/raw_comments.json")


if __name__ == "__main__":
    main()
