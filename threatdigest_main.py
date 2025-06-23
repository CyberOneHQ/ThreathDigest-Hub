# threatdigest_main.py

import os
import logging
from dotenv import load_dotenv

from modules.feed_loader import load_feeds_from_files
from modules.feed_fetcher import fetch_articles_multithreaded
from modules.language_tools import detect_language, translate_text
from modules.deduplicator import deduplicate
from modules.ai_classifier import classify_headline
from modules.utils import get_current_hour_slug, get_today_slug
from modules.output_writer import write_hourly_output, write_daily_output, write_rss_output

# Optional full text if needed in future:
# from modules.article_scraper import extract_full_text

# Load environment variables (for local dev)
load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")

def enrich_articles(raw_articles):
    enriched = []
    for article in raw_articles:
        # Detect language and translate if needed
        lang = detect_language(article["title"])
        if lang != "en":
            translated_title = translate_text(article["title"], to_language="en")
        else:
            translated_title = article["title"]

        # Classify with OpenAI
        classification = classify_headline(translated_title)

        enriched.append({
            "title": translated_title,
            "original_title": article["title"],
            "link": article["link"],
            "published": article["published"],
            "summary": article["summary"],
            "source": article["source"],
            "language": lang,
            "category": classification.get("category", "Unknown"),
            "is_cyber_attack": classification.get("is_cyber_attack", False),
            "confidence": classification.get("confidence", 0),
            "hash": article.get("hash")
        })

    return enriched

def main():
    logging.info("==== Starting ThreatDigest Main Run ====")

    # Load feeds from all configs
    feed_files = [
        "config/feeds_bing.yaml",
        "config/feeds_google.yaml",
        "config/feeds_native.yaml"
    ]
    feeds = load_feeds_from_files(feed_files)

    if not feeds:
        logging.warning("No feeds found. Exiting.")
        return

    # Step 1: Fetch articles
    raw_articles = fetch_articles_multithreaded(feeds)
    if not raw_articles:
        logging.info("No articles fetched.")
        return

    # Step 2: Deduplicate
    unique_articles = deduplicate(raw_articles)
    if not unique_articles:
        logging.info("No new unique articles.")
        return

    # Step 3: Enrich and classify
    enriched_articles = enrich_articles(unique_articles)

    # Step 4: Write output
    hour_slug = get_current_hour_slug()
    day_slug = get_today_slug()

    write_hourly_output(enriched_articles, hour_slug)
    write_daily_output(enriched_articles, day_slug)
    write_rss_output(enriched_articles)

    logging.info("==== ThreatDigest Run Complete ====")

if __name__ == "__main__":
    main()
