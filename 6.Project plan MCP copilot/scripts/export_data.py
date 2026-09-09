"""Copy summary data from the 5 sibling analyst projects into ./data.

Run from this project's root (or anywhere — paths are resolved relative to
this file): `python scripts/export_data.py`

Source projects live as sibling folders of this one inside the Martech
monorepo. This script only reads already-processed summary files (never raw
scraped data) and converts the one SQLite source into JSON so the MCP server
has no database dependency.
"""

import json
import shutil
import sqlite3
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
# Default assumes this project sits directly under Martech/ as a sibling of
# the other numbered project folders. Pass an explicit path as argv[1] to
# override (e.g. when running from a git worktree nested elsewhere).
MARTECH_ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else PROJECT_ROOT.parent
DATA_DIR = PROJECT_ROOT / "data"

SOURCES = [
    (
        MARTECH_ROOT / "1.employee-perception" / "data" / "processed_insights.json",
        DATA_DIR / "employer_perception.json",
    ),
    (
        MARTECH_ROOT / "2.kol-influence-scoring-model" / "data" / "kol_scores.json",
        DATA_DIR / "kol_scores.json",
    ),
    (
        MARTECH_ROOT / "3.survey-social-validation" / "data" / "comparison.json",
        DATA_DIR / "survey_comparison.json",
    ),
    (
        MARTECH_ROOT / "4.Trend Detection Dashboard" / "trend-detection-dashboard" / "data" / "trend_status.json",
        DATA_DIR / "trend_status.json",
    ),
    (
        MARTECH_ROOT / "4.Trend Detection Dashboard" / "trend-detection-dashboard" / "config" / "keywords.json",
        DATA_DIR / "trend_keywords.json",
    ),
]

SCRAPER_DB = MARTECH_ROOT / "5.Automated Scraper + ETL Pipeline" / "data" / "scraped.db"
SCRAPER_JSON_OUT = DATA_DIR / "scraped_channels.json"


def copy_json_sources() -> None:
    for src, dst in SOURCES:
        if not src.exists():
            print(f"  skip (not found): {src}")
            continue
        shutil.copyfile(src, dst)
        print(f"  copied: {src.relative_to(MARTECH_ROOT)} -> {dst.relative_to(PROJECT_ROOT)}")


def export_scraper_db() -> None:
    if not SCRAPER_DB.exists():
        print(f"  skip (not found): {SCRAPER_DB}")
        return
    con = sqlite3.connect(str(SCRAPER_DB))
    con.row_factory = sqlite3.Row
    # The source table currently has duplicate (rank, name) rows — group them
    # away so this project's tool doesn't surface the upstream data-quality bug.
    rows = con.execute(
        "SELECT rank, name, MAX(subscribers) AS subscribers, primary_language, category, "
        "country, youtube_url, MAX(scraped_at) AS scraped_at FROM channels "
        "GROUP BY rank, name ORDER BY rank"
    ).fetchall()
    con.close()
    payload = {
        "source": "Wikipedia list of most-subscribed YouTube channels (scraped)",
        "scraped_at": rows[0]["scraped_at"] if rows else None,
        "channels": [dict(r) for r in rows],
    }
    SCRAPER_JSON_OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  exported {len(rows)} rows -> {SCRAPER_JSON_OUT.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    DATA_DIR.mkdir(exist_ok=True)
    print("Copying processed JSON summaries...")
    copy_json_sources()
    print("Exporting scraped.db -> JSON...")
    export_scraper_db()
    print("Done.")
