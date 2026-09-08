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
        "youtube_queries": ["Agoda employee review interview", "Agoda Thailand office life"],
        "youtube_match_terms": ["agoda"],
        "news_query": "Agoda",
    },
    {
        "name": "Shopee Thailand",
        "reddit_subreddits": ["thailand", "bangkok", "AskThailand"],
        "reddit_query": "Shopee Thailand OR \"Shopee\"",
        "youtube_queries": [
            "Shopee Thailand employee review interview",
            "Shopee Thailand office culture life",
            "ทำงานที่ Shopee รีวิวพนักงาน",
            "Shopee สัมภาษณ์งาน",
        ],
        "youtube_match_terms": ["shopee"],
        "news_query": "\"Shopee\" Thailand",
    },
    {
        "name": "Grab Thailand",
        "reddit_subreddits": ["thailand", "bangkok", "AskThailand"],
        "reddit_query": "Grab Thailand OR \"Grab\"",
        "youtube_queries": [
            "Grab Thailand employee review interview",
            "Grab Thailand office culture life",
            "ทำงานที่ Grab รีวิวพนักงาน",
            "Grab สัมภาษณ์งาน",
        ],
        "youtube_match_terms": ["grab"],
        "news_query": "\"Grab\" Thailand",
    },
]
