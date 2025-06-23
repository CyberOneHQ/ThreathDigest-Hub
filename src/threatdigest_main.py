import os
import yaml
import hashlib
import logging
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

# Cache for hashes to skip duplicates
dedup_cache = set()

def hash_article(article):
    data = (article.get("title") or "") + (article.get("link") or "")
    return hashlib.sha256(data.encode("utf-8")).hexdigest()

def process_articles(articles):
    enriched = []
    for article in articles:
        hash_val = hash_article(article)
        if hash_val in dedup_cache:
            continue
        dedup_cache.add(hash_val)

        lang = detect_language(article["title"])
        if lang != "en":
            translated = translate_text(article["title"], lang)
            article["translated_title"] = translated
        else:
            article["translated_title"] = article["title"]

        classification = classify_headline(article["translated_title"])

        article["classification"] = classification
        article["processed_at"] = datetime.utcnow().isoformat()
        enriched.append(article)
    return enriched

def main():
    logging.info("=== ThreatDigest Main Run Started ===")
    
    feeds_file = "src/config/threatdigest.yml"
    feed_config = load_yaml_file(feeds_file)

    all_articles = fetch_articles_multithreaded(feed_config)
    logging.info(f"Fetched {len(all_articles)} articles")

    processed = process_articles(all_articles)
    logging.info(f"Processed and classified {len(processed)} articles")

    # For now, just print titles classified as cyberattacks
    for article in processed:
        if article.get("classification", {}).get("is_cyber_attack"):
            logging.info(f"[CYBER] {article['title']} → {article['classification']}")

    ensure_output_directory()
    # Extend here to write JSON/RSS/Markdown outputs

if __name__ == "__main__":
    main()
