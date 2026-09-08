"""Run all three collectors in sequence, writing into data/raw_comments.json."""

import collect_news
import collect_reddit
import collect_youtube

if __name__ == "__main__":
    collect_reddit.main()
    collect_youtube.main()
    collect_news.main()
