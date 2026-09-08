"""Shared constants for the KOL scoring pipeline."""

import json
import os

SCRIPT_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(SCRIPT_DIR, "..", "data")

KOL_LIST_PATH = os.path.join(DATA_DIR, "kol_list.json")
RAW_STATS_PATH = os.path.join(DATA_DIR, "raw_kol_stats.json")
SCORES_PATH = os.path.join(DATA_DIR, "kol_scores.json")

VIDEOS_PER_KOL = 15

# Composite score weights — see README for the reasoning behind these numbers.
WEIGHT_ENGAGEMENT_RATE = 0.4
WEIGHT_AVG_VIEWS = 0.3
WEIGHT_UPLOAD_FREQUENCY = 0.3


def load_kol_list() -> list[dict]:
    with open(KOL_LIST_PATH, encoding="utf-8") as f:
        return json.load(f)["kols"]
