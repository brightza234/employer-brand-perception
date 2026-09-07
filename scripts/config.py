"""Shared config: target companies and per-source search terms."""

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
