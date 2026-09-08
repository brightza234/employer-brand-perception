"""Collect channel + recent video statistics for every KOL in data/kol_list.json.

For each channel we pull:
  - current subscriber_count (channels.list statistics)
  - the uploads playlist ID (channels.list contentDetails)
  - the most recent VIDEOS_PER_KOL videos from that playlist, with view/like/comment
    counts, publish date, title and description (used later for both engagement
    metrics and Claude content-theme classification)

Usage:
    python scripts/collect_youtube.py

Requires YOUTUBE_API_KEY in .env.local.
"""

import datetime
import json
import os
import sys

from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

sys.path.insert(0, os.path.dirname(__file__))
from config import RAW_STATS_PATH, VIDEOS_PER_KOL, load_kol_list


def fetch_channel(youtube, handle: str) -> dict | None:
    response = youtube.channels().list(part="snippet,statistics,contentDetails", forHandle=handle.lstrip("@")).execute()
    items = response.get("items", [])
    if not items:
        print(f"[youtube]   handle {handle} not found — skipping")
        return None
    item = items[0]
    return {
        "channel_id": item["id"],
        "title": item["snippet"]["title"],
        "subscriber_count": int(item["statistics"].get("subscriberCount", 0)),
        "uploads_playlist_id": item["contentDetails"]["relatedPlaylists"]["uploads"],
    }


def fetch_recent_video_ids(youtube, uploads_playlist_id: str, max_results: int) -> list[str]:
    response = (
        youtube.playlistItems()
        .list(part="contentDetails", playlistId=uploads_playlist_id, maxResults=max_results)
        .execute()
    )
    return [item["contentDetails"]["videoId"] for item in response.get("items", [])]


def fetch_video_stats(youtube, video_ids: list[str]) -> list[dict]:
    if not video_ids:
        return []
    response = youtube.videos().list(part="snippet,statistics", id=",".join(video_ids)).execute()
    videos = []
    for item in response.get("items", []):
        stats = item["statistics"]
        videos.append(
            {
                "video_id": item["id"],
                "title": item["snippet"]["title"],
                "description": item["snippet"]["description"],
                "published_at": item["snippet"]["publishedAt"],
                "view_count": int(stats.get("viewCount", 0)),
                "like_count": int(stats.get("likeCount", 0)),
                "comment_count": int(stats.get("commentCount", 0)),
            }
        )
    return videos


def collect_for_kol(youtube, kol: dict) -> dict | None:
    channel = fetch_channel(youtube, kol["handle"])
    if channel is None:
        return None
    video_ids = fetch_recent_video_ids(youtube, channel["uploads_playlist_id"], VIDEOS_PER_KOL)
    videos = fetch_video_stats(youtube, video_ids)
    return {
        "handle": kol["handle"],
        "display_name": kol.get("display_name", channel["title"]),
        "channel_id": channel["channel_id"],
        "subscriber_count": channel["subscriber_count"],
        "videos": videos,
    }


def main() -> None:
    load_dotenv(".env.local")
    api_key = os.environ.get("YOUTUBE_API_KEY")
    if not api_key:
        print("[youtube] YOUTUBE_API_KEY not set in .env.local — aborting")
        sys.exit(1)
    youtube = build("youtube", "v3", developerKey=api_key)

    kols = load_kol_list()
    results = []
    for kol in kols:
        print(f"[youtube] fetching {kol['display_name']} ({kol['handle']})...")
        try:
            record = collect_for_kol(youtube, kol)
        except HttpError as e:
            print(f"[youtube]   API error for {kol['handle']}: {e}")
            continue
        if record is not None:
            print(f"[youtube]   {record['subscriber_count']:,} subs, {len(record['videos'])} videos")
            results.append(record)

    snapshot = {
        "collected_at": datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z"),
        "kols": results,
    }
    os.makedirs(os.path.dirname(RAW_STATS_PATH), exist_ok=True)
    with open(RAW_STATS_PATH, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, ensure_ascii=False, indent=2)
    print(f"[youtube] done. {len(results)}/{len(kols)} KOLs saved to {RAW_STATS_PATH}")


if __name__ == "__main__":
    main()
