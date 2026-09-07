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

VIDEOS_PER_COMPANY = 10
COMMENTS_PER_VIDEO = 50


def search_videos(youtube, query: str, max_results: int) -> list[str]:
    response = (
        youtube.search()
        .list(q=query, part="id", type="video", maxResults=max_results, relevanceLanguage="en")
        .execute()
    )
    return [item["id"]["videoId"] for item in response.get("items", [])]


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
    video_ids = search_videos(youtube, company["youtube_query"], VIDEOS_PER_COMPANY)

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
                    "collected_at": datetime.datetime.utcnow().isoformat() + "Z",
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
