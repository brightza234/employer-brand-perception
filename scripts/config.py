"""Shared config: target companies, search terms, and analysis taxonomy."""

THEMES = [
    "Compensation & Benefits",
    "Work-Life Balance",
    "Management & Leadership",
    "Career Growth & Development",
    "Company Culture",
    "Job Security & Stability",
]

SENTIMENTS = ["positive", "neutral", "negative"]

COMPANIES = [
    {
        "name": "Agoda",
        "reddit_subreddits": ["thailand", "bangkok", "AskThailand", "cscareerquestions", "ExperiencedDevs"],
        "reddit_query": "Agoda",
        "youtube_query": "working at Agoda review",
        "news_query": "Agoda",
    },
    {
        "name": "True Digital Group",
        "reddit_subreddits": ["thailand", "bangkok", "AskThailand"],
        "reddit_query": "True Digital Group OR \"True Digital\"",
        "youtube_query": "True Digital Group review employee",
        "news_query": "\"True Digital Group\"",
    },
    {
        "name": "SCBX",
        "reddit_subreddits": ["thailand", "bangkok", "AskThailand"],
        "reddit_query": "SCBX OR \"SCB X\" OR \"Siam Commercial Bank\"",
        "youtube_query": "SCBX SCB working review employee",
        "news_query": "SCBX OR \"SCB X\"",
    },
]
