"""Classify each KOL's recent videos into a content theme using the Claude API.

Why an LLM instead of keyword rules: Thai tech-review titles mix languages,
slang, and emoji ("ป้ายยา", "ลองมา 2 อาทิตย์") in ways that make brittle keyword
matching miss most videos. One classification call per KOL (all ~15 videos at
once) keeps this cheap — classification is a simple, well-specified task, so a
small/fast model (Haiku) is the right cost/quality tradeoff, not Opus.

Usage:
    python scripts/classify_themes.py

Requires ANTHROPIC_API_KEY in .env.local.
"""

import json
import os
import re
import sys

import anthropic
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(__file__))
from config import RAW_STATS_PATH

MODEL = "claude-haiku-4-5"
THEMES = [
    "Smartphone",
    "Laptop/PC",
    "Wearable/Gadget",
    "Home Appliance/Audio",
    "Tech News/Update",
    "Other/Lifestyle",
]
THEMES_PATH = os.path.join(os.path.dirname(RAW_STATS_PATH), "content_themes.json")

SYSTEM_PROMPT = f"""You classify Thai/English YouTube tech-review video titles into exactly one \
content theme per video. Allowed themes: {", ".join(THEMES)}.

Reply with ONLY a JSON array, one object per input video in the same order, each \
shaped like {{"video_id": "...", "theme": "..."}}. No prose, no markdown fences."""


def build_user_message(videos: list[dict]) -> str:
    lines = [f'{{"video_id": "{v["video_id"]}", "title": {json.dumps(v["title"])}}}' for v in videos]
    return "Classify these videos:\n" + "\n".join(lines)


def parse_json_array(text: str) -> list[dict]:
    match = re.search(r"\[.*\]", text, re.DOTALL)
    if not match:
        raise ValueError(f"no JSON array found in response: {text[:200]!r}")
    return json.loads(match.group(0))


def classify_kol_videos(client: anthropic.Anthropic, videos: list[dict]) -> dict[str, str]:
    if not videos:
        return {}
    response = client.messages.create(
        model=MODEL,
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": build_user_message(videos)}],
    )
    text = next((b.text for b in response.content if b.type == "text"), "")
    try:
        classified = parse_json_array(text)
    except (ValueError, json.JSONDecodeError) as e:
        print(f"[themes]   failed to parse classification response: {e}")
        return {}
    return {item["video_id"]: item["theme"] for item in classified if item.get("theme") in THEMES}


def main() -> None:
    load_dotenv(".env.local")
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("[themes] ANTHROPIC_API_KEY not set in .env.local — aborting")
        sys.exit(1)

    with open(RAW_STATS_PATH, encoding="utf-8") as f:
        snapshot = json.load(f)

    client = anthropic.Anthropic()
    result = {}
    for kol in snapshot["kols"]:
        print(f"[themes] classifying {kol['display_name']} ({len(kol['videos'])} videos)...")
        video_themes = classify_kol_videos(client, kol["videos"])
        theme_counts: dict[str, int] = {}
        for theme in video_themes.values():
            theme_counts[theme] = theme_counts.get(theme, 0) + 1
        result[kol["handle"]] = {
            "display_name": kol["display_name"],
            "video_themes": video_themes,
            "theme_breakdown": theme_counts,
        }

    os.makedirs(os.path.dirname(THEMES_PATH), exist_ok=True)
    with open(THEMES_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"[themes] done. wrote {THEMES_PATH}")


if __name__ == "__main__":
    main()
