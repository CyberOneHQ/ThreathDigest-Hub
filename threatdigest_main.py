# ==== Module Imports ====
import os
import logging
from datetime import datetime

# ==== Local Modules ====
from modules.feed_fetcher import fetch_articles
from modules.feed_loader import load_feeds_from_files
from modules.deduplicator import deduplicate_articles
from modules.language_tools import detect_language, translate_text
from modules.article_scraper import extract_article_content
from modules.ai_summarizer import summarize_content 
from modules.logger_utils import setup_logger, log_article_summary
from modules.ai_classifier import classify_article
from modules.output_writer import (
    write_hourly_output,
    write_daily_output,
    write_rss_output,
)
from modules.utils import get_current_hour_slug, get_today_slug

# ==== Article Enrichment ====
def enrich_articles(articles, summarize=False):
    enriched = []

    for article in articles:
        lang = detect_language(article["title"])
        translated_title = translate_text(article["title"], lang="en")

        classification = classify_article(translated_title)

        # Extract full content
        full_content = extract_article_content(article["link"])
        if full_content:
            logging.info(f"Extracted {len(full_content)} characters from {article['link']}")
        else:
            logging.warning(f"No content extracted from {article['link']}")

        # GPT summarization
        summary = ""
        if summarize and full_content:
            try:
                summary = summarize_content(full_content)
                log_article_summary(article["link"], summary)
            except Exception as e:
                logging.error(f"Summary failed for {article['link']}: {e}")

        article.update({
            "translated_title": translated_title,
            "language": lang,
            "is_cyber_attack": classification.get("is_cyber_attack", False),
            "category": classification.get("category", "Unknown"),
            "confidence": classification.get("confidence", 0),
            "full_content": full_content,
            "summary_gpt": summary,
            "timestamp": datetime.utcnow().isoformat()
        })

        if article["is_cyber_attack"]:
            enriched.append(article)

    return enriched

# ==== Main Execution ====
def main():
    setup_logger()
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
    if not unique_articles:
        logging.info("No new articles after deduplication.")
        return

    # Step 4: Enrich with classification, scraping, translation, GPT
    enriched_articles = enrich_articles(unique_articles, summarize=True)
    if not enriched_articles:
        logging.info("No cyberattack-related articles after enrichment.")
        return

    # Step 5: Output to files
    write_hourly_output(enriched_articles)
    write_daily_output(enriched_articles)
    write_rss_output(enriched_articles)

    logging.info("==== ThreatDigest Run Complete ====")

if __name__ == "__main__":
    main()
