import os
import logging
import hashlib
from datetime import datetime
from modules.feed_fetcher import fetch_articles_multithreaded
from modules.language_tools import detect_language, translate_text
from modules.ai_classifier import classify_headline
from modules.utils import load_yaml_file, ensure_output_directory

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logs/threatdigest.log"),
        logging.StreamHandler()
    ]
)

# Deduplication cache
dedup_cache = set()

def hash_article(article):
    title = article.get("title", "")
    link = article.get("link", "")
    return hashlib.sha256((title + link).encode("utf-8")).hexdigest()

def process_articles(articles):
    processed = []
    for article in articles:
        article_hash = hash_article(article)
        if article_hash in dedup_cache:
            logging.debug(f"Skipped duplicate: {article['title']}")
            continue
        dedup_cache.add(article_hash)

        # Detect and translate if needed
        lang = detect_language(article["title"])
        if lang != "en":
            article["translated_title"] = translate_text(article["title"], lang)
        else:
            article["translated_title"] = article["title"]

        # Classify
        classification = classify_headline(article["translated_title"])
        article["classification"] = classification
        article["processed_at"] = datetime.utcnow().isoformat()

        # Append only if classified as cyberattack
        if classification.get("is_cyber_attack"):
            processed.append(article)
            logging.info(f"[CYBER] {article['translated_title']} → {classification}")
        else:
            logging.debug(f"[SKIP] {article['translated_title']} → {classification}")

    return processed

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

    ensure_output_directory()

    # You can optionally write to JSON/RSS here
    # Example: write_json(enriched), write_rss(enriched)

if __name__ == "__main__":
    main()
