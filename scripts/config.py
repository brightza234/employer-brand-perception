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
        "name": "True Digital Group",
        "reddit_subreddits": ["thailand", "bangkok", "AskThailand"],
        "reddit_query": "True Digital Group OR \"True Digital\"",
        "youtube_queries": [
            "\"True Digital Group\" employee review interview",
            "True Digital Park internship office",
            "ทรู ดิจิทัล พาร์ค รีวิว พนักงาน",
            "ทำงานที่ True Digital",
        ],
        "youtube_match_terms": ["true digital", "ทรู ดิจิทัล"],
        "news_query": "\"True Digital Group\"",
    },
    {
        "name": "SCBX",
        "reddit_subreddits": ["thailand", "bangkok", "AskThailand"],
        "reddit_query": "SCBX OR \"SCB X\" OR \"Siam Commercial Bank\"",
        "youtube_queries": [
            "SCBX SCB employee review interview",
            "SCB TechX employee",
            "SCB DataX employee",
            "SCBX ทำงานที่ รีวิวพนักงาน",
            "ไทยพาณิชย์ สัมภาษณ์งาน พนักงาน",
        ],
        "youtube_match_terms": [
            "scbx",
            "scb x",
            "siam commercial bank",
            "scb techx",
            "scb datax",
            "ไทยพาณิชย์",
        ],
        "news_query": "SCBX OR \"SCB X\"",
    },
]
