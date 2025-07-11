# ==== Module Imports ====
import os
import json
import logging
from pathlib import Path
from datetime import datetime
from feedgen.feed import FeedGenerator

# ==== Output Paths ====
BASE_OUTPUT = Path(__file__).parent.parent / "data" / "output"
HOURLY_DIR = BASE_OUTPUT / "hourly"
DAILY_DIR = BASE_OUTPUT / "daily"
RSS_PATH = BASE_OUTPUT / "rss_cyberattacks.xml"
STATIC_HOURLY = BASE_OUTPUT / "hourly_latest.json"
STATIC_DAILY = BASE_OUTPUT / "daily_latest.json"

# ==== Directory Helper ====
def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

# ==== JSON Writer ====
def write_json(data, path):
    ensure_dir(path.parent)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    logging.info(f"Saved JSON to {path}")

# ==== Write Hourly Output ====
def write_hourly_output(articles):
    timestamp = datetime.utcnow().strftime("%Y-%m-%d_%H")
    filename = f"{timestamp}.json"
    hourly_path = HOURLY_DIR / filename
    write_json(articles, hourly_path)
    write_json(articles, STATIC_HOURLY)

# ==== Write Daily Output ====
def write_daily_output(articles):
    date = datetime.utcnow().strftime("%Y-%m-%d")
    filename = f"{date}.json"
    daily_path = DAILY_DIR / filename
    write_json(articles, daily_path)
    write_json(articles, STATIC_DAILY)

# ==== Write RSS Feed ====
def write_rss_output(articles):
    fg = FeedGenerator()
    fg.id("https://yourdomain.com/threatdigest")
    fg.title("ThreatDigest Hub - Curated Cyber Incidents")
    fg.link(href="https://yourdomain.com", rel="self")
    fg.language("en")
    fg.description("A curated list of recent cyber incidents, attacks, and security threats.")

    for article in articles:
        fe = fg.add_entry()
        fe.title(article.get("title", "No Title"))
        fe.link(href=article.get("link", "#"))
        fe.description(article.get("summary", "No summary available."))
        fe.pubDate(article.get("published", datetime.utcnow().isoformat()))

    ensure_dir(RSS_PATH.parent)
    fg.rss_file(str(RSS_PATH))
    logging.info(f"RSS feed saved to {RSS_PATH}")
