"""AI Analyst Copilot MCP server.

Exposes read-only tools over the summary data exported from 5 prior
analyst projects (see scripts/export_data.py). Transport is stdio, so it
runs as a local subprocess launched by an MCP client (Claude Desktop, the
MCP Inspector, etc) — no hosting required.
"""

import json
from functools import lru_cache
from pathlib import Path

from fastmcp import FastMCP

DATA_DIR = Path(__file__).resolve().parent / "data"

mcp = FastMCP("analyst-copilot")


@lru_cache(maxsize=None)
def _load(filename: str) -> dict:
    path = DATA_DIR / filename
    return json.loads(path.read_text(encoding="utf-8"))


@mcp.tool()
def get_employer_perception(company: str) -> dict:
    """Employer-brand sentiment/theme breakdown from scraped employee reviews.

    Args:
        company: Company name (case-insensitive, e.g. "Agoda").
    """
    data = _load("employer_perception.json")
    companies = data.get("companies", {})
    match = next((name for name in companies if name.lower() == company.lower()), None)
    if match is None:
        return {
            "error": f"No employer-perception data for '{company}'.",
            "available_companies": sorted(companies.keys()),
        }
    record = companies[match]
    return {
        "company": match,
        "generated_at": data.get("generated_at"),
        "total_comments": record.get("total_comments"),
        "sentiment_distribution": record.get("sentiment_distribution"),
        "theme_distribution": record.get("theme_distribution"),
        "trend": record.get("trend"),
        "caveat": (
            f"Based on {record.get('total_comments')} classified comments out of "
            f"{record.get('total_raw_comments')} raw scraped comments (Reddit/YouTube/News) — "
            "self-selected public posters, not a representative employee sample."
        ),
    }


@mcp.tool()
def get_kol_score(channel: str) -> dict:
    """Composite influence score (0-1470 subscriber-scale) for a Thai tech-content KOL.

    Args:
        channel: YouTube handle (with or without @) or display name, e.g. "@iHAVECPU_".
    """
    data = _load("kol_scores.json")
    kols = data.get("kols", [])
    needle = channel.lower().lstrip("@")
    match = next(
        (k for k in kols if k["handle"].lower().lstrip("@") == needle or needle in k["display_name"].lower()),
        None,
    )
    if match is None:
        return {
            "error": f"No KOL score for '{channel}'.",
            "available_channels": [k["handle"] for k in kols],
        }
    return {
        **match,
        "weights": data.get("weights"),
        "computed_at": data.get("computed_at"),
        "caveat": (
            f"composite_score is a weighted z-score computed relative to the other "
            f"{len(kols)} channels in this peer set (weights: {data.get('weights')}) — "
            "it is a relative ranking, not an absolute or cross-cohort comparable score."
        ),
    }


@mcp.tool()
def get_trend_status(keyword: str) -> dict:
    """Trend/mention status for a tracked consumer-tech keyword.

    Args:
        keyword: Tracked keyword, e.g. "iPhone 17".
    """
    status = _load("trend_status.json")
    tracked = _load("trend_keywords.json").get("keywords", [])
    series = status.get("keywords", {})
    match = next((k for k in series if k.lower() == keyword.lower()), None)
    if match is None:
        note = (
            "No trend data collected yet for this keyword — the trend-detection "
            "pipeline has not run against it."
            if keyword in tracked
            else f"'{keyword}' is not in the tracked keyword list."
        )
        return {
            "error": note,
            "tracked_keywords": tracked,
        }
    return {
        "keyword": match,
        "generated_at": status.get("generated_at"),
        **series[match],
        "caveat": "Mention counts reflect scraped-source coverage only, not total market conversation volume.",
    }


@mcp.tool()
def get_survey_validation(theme: str) -> dict:
    """Compares an HR-survey-derived theme ranking against social-listening volume/sentiment.

    Args:
        theme: Theme name, e.g. "Work-Life Balance", "Career Growth", "Management/Relationship".
    """
    data = _load("survey_comparison.json")
    themes = data.get("themes", [])
    match = next((t for t in themes if t["theme"].lower() == theme.lower()), None)
    if match is None:
        return {
            "error": f"No survey-validation data for theme '{theme}'.",
            "available_themes": [t["theme"] for t in themes],
        }
    return {
        **match,
        "reliability": data.get("reliability"),
        "rank_agreement": data.get("rank_agreement"),
        "n_dataset_rows": data.get("n_dataset_rows"),
        "n_social_comments_classified": data.get("n_social_comments_classified"),
        "caveat": (
            "Survey respondents are self-selected (self-selection bias) and may under-report "
            "sensitive dissatisfaction (social desirability bias); social comments skew toward "
            "people motivated enough to post publicly. Treat rank_gap as a discussion prompt, "
            "not proof either source is 'wrong'."
        ),
    }


@mcp.tool()
def query_scraped_data(query: str = "") -> dict:
    """Search the scraped top-200 most-subscribed YouTube channels dataset.

    Args:
        query: Free-text substring matched against channel name, category, country,
            or primary language. Empty string returns the top-ranked channels.
    """
    data = _load("scraped_channels.json")
    channels = data.get("channels", [])
    if not query.strip():
        results = channels[:10]
    else:
        needle = query.lower()
        results = [
            c
            for c in channels
            if needle in c["name"].lower()
            or needle in (c.get("category") or "").lower()
            or needle in (c.get("country") or "").lower()
            or needle in (c.get("primary_language") or "").lower()
        ]
    return {
        "query": query,
        "matched": len(results),
        "results": results[:20],
        "source": data.get("source"),
        "scraped_at": data.get("scraped_at"),
        "caveat": "Snapshot scraped at a single point in time from Wikipedia — subscriber counts drift daily.",
    }


if __name__ == "__main__":
    mcp.run()
