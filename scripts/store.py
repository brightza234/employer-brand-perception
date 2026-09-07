"""Shared helpers for reading/writing data/raw_comments.json.

Record schema: {id, source, company, text, date, url, collected_at}
`id` is a hash of source+url+text so re-running a collector merges instead
of duplicating records.
"""

import hashlib
import json
import os

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "raw_comments.json")


def make_id(source: str, url: str, text: str) -> str:
    key = f"{source}|{url}|{text[:200]}"
    return hashlib.sha1(key.encode("utf-8")).hexdigest()[:16]


def load_records() -> dict:
    if not os.path.exists(DATA_PATH):
        return {}
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        records = json.load(f)
    return {r["id"]: r for r in records}


def save_records(records_by_id: dict) -> None:
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    records = sorted(records_by_id.values(), key=lambda r: r["date"], reverse=True)
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)


def merge_new_records(new_records: list[dict]) -> tuple[int, int]:
    """Merge new_records into data/raw_comments.json. Returns (added, total)."""
    existing = load_records()
    added = 0
    for r in new_records:
        if r["id"] not in existing:
            added += 1
        existing[r["id"]] = r
    save_records(existing)
    return added, len(existing)
