"""Collect YouTube comments from videos related to target companies.

Usage:
    python scripts/collect_youtube.py

Requires YOUTUBE_API_KEY in .env.local.
"""

import datetime
import os
import sys

from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

sys.path.insert(0, os.path.dirname(__file__))
from config import COMPANIES
from store import make_id, merge_new_records

VIDEOS_PER_QUERY = 15
COMMENTS_PER_VIDEO = 50


def search_videos(youtube, query: str, match_terms: list[str], max_results: int) -> list[str]:
    """Search for videos and keep only ones whose title actually mentions the company —
    YouTube's search endpoint ranks loosely on multi-word queries and otherwise returns
    plenty of irrelevant results."""
    response = (
        youtube.search()
        .list(q=query, part="snippet", type="video", maxResults=max_results)
        .execute()
    )
    video_ids = []
    for item in response.get("items", []):
        title = item["snippet"]["title"].lower()
        if any(term in title for term in match_terms):
            video_ids.append(item["id"]["videoId"])
    return video_ids


def collect_comments(youtube, video_id: str, max_results: int) -> list[dict]:
    comments = []
    try:
        response = (
            youtube.commentThreads()
            .list(part="snippet", videoId=video_id, maxResults=max_results, textFormat="plainText", order="relevance")
            .execute()
        )
    except HttpError as e:
        # comments disabled on this video, or quota-related issue
        print(f"[youtube]   skipping video {video_id}: {e.reason if hasattr(e, 'reason') else e}")
        return comments

    for item in response.get("items", []):
        top = item["snippet"]["topLevelComment"]["snippet"]
        comments.append(
            {
                "text": top["textDisplay"],
                "date": top["publishedAt"],
                "url": f"https://www.youtube.com/watch?v={video_id}&lc={item['snippet']['topLevelComment']['id']}",
            }
        )
    return comments


def collect_for_company(youtube, company: dict) -> list[dict]:
    records = []
    video_ids: set[str] = set()
    for query in company["youtube_queries"]:
        video_ids.update(search_videos(youtube, query, company["youtube_match_terms"], VIDEOS_PER_QUERY))

    for video_id in video_ids:
        for comment in collect_comments(youtube, video_id, COMMENTS_PER_VIDEO):
            records.append(
                {
                    "id": make_id("youtube", comment["url"], comment["text"]),
                    "source": "youtube",
                    "company": company["name"],
                    "text": comment["text"],
                    "date": comment["date"],
                    "url": comment["url"],
                    "collected_at": datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z"),
                }
            )

    return records


def main() -> None:
    load_dotenv(".env.local")
    api_key = os.environ.get("YOUTUBE_API_KEY")
    if not api_key:
        print("[youtube] skipping — YOUTUBE_API_KEY not set in .env.local")
        return
    youtube = build("youtube", "v3", developerKey=api_key)

    all_records = []
    for company in COMPANIES:
        print(f"[youtube] searching for {company['name']}...")
        company_records = collect_for_company(youtube, company)
        print(f"[youtube] {company['name']}: {len(company_records)} records")
        all_records.extend(company_records)

    added, total = merge_new_records(all_records)
    print(f"[youtube] done. added {added} new records, {total} total in data/raw_comments.json")


if __name__ == "__main__":
    main()
