#ThreathDigest-Hub/threatdigest_main.py

import os
import logging
from datetime import datetime
from modules.feed_fetcher import fetch_articles
from modules.feed_loader import load_feeds_from_files
from modules.deduplicator import deduplicate_articles
from modules.language_tools import detect_language, translate_text
from modules.ai_classifier import classify_article
from modules.output_writer import (
    write_hourly_output,
    write_daily_output,
    write_rss_output,
)
from modules.utils import get_current_hour_slug, get_today_slug

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
)

def enrich_articles(articles):
    enriched = []
    for article in articles:
        lang = detect_language(article["title"])
        translated_title = translate_text(article["title"], lang="en")

        classification = classify_headline(translated_title)
        article.update({
            "translated_title": translated_title,
            "language": lang,
            "is_cyber_attack": classification.get("is_cyber_attack", False),
            "category": classification.get("category", "Unknown"),
            "confidence": classification.get("confidence", 0),
            "timestamp": datetime.utcnow().isoformat()
        })
        enriched.append(article)
    return enriched

def main():
    logging.info("==== Starting ThreatDigest Main Run ====")

    # Step 1: Load feeds
    feed_paths = [
        "config/feeds_bing.yaml",
        "config/feeds_google.yaml",
        "config/feeds_native.yaml"
    ]
    all_feeds = load_feeds_from_files(feed_paths)
    if not all_feeds:
        logging.warning("No feeds found. Exiting.")
        return

    # Step 2: Fetch raw articles
    raw_articles = fetch_articles(all_feeds)
    if not raw_articles:
        logging.warning("No articles fetched.")
        return

    # Step 3: Deduplicate
    unique_articles = deduplicate_articles(raw_articles)
    logging.info(f"Deduplicated articles. Unique entries: {len(unique_articles)}")

    if not unique_articles:
        logging.info("No new articles after deduplication.")
        return

    # Step 4: Enrich
    enriched_articles = enrich_articles(unique_articles)

    # Step 5: Output
    hour_slug = get_current_hour_slug()
    day_slug = get_today_slug()

    write_hourly_output(enriched_articles, hour_slug)
    write_daily_output(enriched_articles, day_slug)
    write_rss_output(enriched_articles)

    logging.info("==== ThreatDigest Run Complete ====")

if __name__ == "__main__":
    main()
