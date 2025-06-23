import os
import logging
import hashlib
from datetime import datetime
from modules.feed_fetcher import fetch_articles_multithreaded
from modules.language_tools import detect_language, translate_text
from modules.ai_classifier import classify_headline
from modules.utils import load_yaml_file, ensure_output_directory, write_json_file
from modules.deduplicator import deduplicate
from modules.feed_writer import generate_rss_output

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logs/threatdigest.log"),
        logging.StreamHandler()
    ]
)

# Deduplication cache for this session
session_hash_cache = set()

def hash_article(article):
    title = article.get("title", "")
    link = article.get("link", "")
    return hashlib.sha256((title + link).encode("utf-8")).hexdigest()

def process_articles(articles):
    processed = []
    for article in articles:
        article_hash = hash_article(article)
        if article_hash in session_hash_cache:
            logging.debug(f"Skipped session duplicate: {article['title']}")
            continue
        session_hash_cache.add(article_hash)

        # Detect language and translate
        lang = detect_language(article["title"])
        article["language"] = lang
        article["translated_title"] = translate_text(article["title"], lang) if lang != "en" else article["title"]

        # Classify with AI
        classification = classify_headline(article["translated_title"])
        article["classification"] = classification
        article["processed_at"] = datetime.utcnow().isoformat()

        if classification.get("is_cyber_attack"):
            processed.append(article)
            logging.info(f"[CYBER] {article['translated_title']} → {classification}")
        else:
            logging.debug(f"[SKIP] {article['translated_title']} → {classification}")

    return processed

def write_outputs(enriched_articles):
    ensure_output_directory()
    timestamp = datetime.utcnow()
    date_str = timestamp.strftime("%Y-%m-%d")
    hour_str = timestamp.strftime("%Y-%m-%d_%H")

    hourly_path = os.path.join("data", "output", "hourly", f"{hour_str}.json")
    daily_path = os.path.join("data", "output", "daily", f"{date_str}.json")
    aggregate_path = os.path.join("data", "output", "aggregate", "master.json")

    write_json_file(hourly_path, enriched_articles)
    write_json_file(daily_path, enriched_articles)
    write_json_file(aggregate_path, enriched_articles)  # This can be replaced periodically with a rollup

    generate_rss_output(enriched_articles)

def main():
    logging.info("=== ThreatDigest Run Started ===")

    feeds_path = "config/threatdigest.yml"
    if not os.path.exists(feeds_path):
        logging.error("Feed config not found at config/threatdigest.yml")
        return

    feeds = load_yaml_file(feeds_path)
    all_articles = fetch_articles_multithreaded(feeds)
    logging.info(f"Fetched {len(all_articles)} articles from feeds")

    enriched = process_articles(all_articles)
    logging.info(f"{len(enriched)} articles classified as cyberattacks")

    unique = deduplicate(enriched)
    write_outputs(unique)

    logging.info("=== ThreatDigest Run Complete ===")

if __name__ == "__main__":
    main()
