import os
import sys
import logging
import concurrent.futures
from datetime import datetime

# Ensure modules directory is accessible
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Modules imports
from modules.feed_fetcher import load_all_feeds
from modules.deduplicator import deduplicate
from modules.article_scraper import extract_full_text
from modules.azure_translator import translate_text
from modules.ai_classifier import classify_article
from modules.feed_writer import generate_rss_output

# Setup logging
logging.basicConfig(
    filename=os.path.join(os.path.dirname(__file__), '../data/state/threatdigest.log'),
    filemode='a',
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s'
)

def fetch_and_process_feed(feed):
    from feedparser import parse
    try:
        parsed_feed = parse(feed['url'])
        entries = []
        for entry in parsed_feed.entries:
            entries.append({
                'title': entry.title,
                'link': entry.link,
                'source': feed.get('source', 'unknown'),
                'region': feed.get('region', 'unknown'),
                'category': feed.get('category', 'unknown')
            })
        logging.info(f"Fetched {len(entries)} entries from {feed['url']}")
        return entries
    except Exception as e:
        logging.error(f"Failed fetching from {feed['url']}: {e}")
        return []

def main():
    logging.info("ThreatDigest Hub started")
    print("[*] Loading feeds configuration...")

    # Step 1: Unified YAML loading
    feeds = load_all_feeds()
    logging.info(f"Total feeds loaded: {len(feeds)}")

    # Step 2: Multithreaded RSS feed fetching
    print("[*] Fetching articles from feeds (multithreaded)...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        results = executor.map(fetch_and_process_feed, feeds)

    # Flatten results
    articles = [article for sublist in results for article in sublist]
    logging.info(f"Total articles fetched: {len(articles)}")

    # Step 3: Deduplication (SHA-256 hashing)
    print("[*] Deduplicating articles...")
    articles = deduplicate(articles)
    logging.info(f"Articles after deduplication: {len(articles)}")

    # Step 4: Language detection and translation (Azure Translator)
    print("[*] Translating non-English headlines...")
    for article in articles:
        article['translated_title'] = translate_text(article['title'], to_language='en')

    # Step 5: GPT-based classification & IOC extraction
    print("[*] Classifying articles and extracting metadata...")
    for article in articles:
        content = extract_full_text(article['link']) or article['translated_title']
        classification = classify_article(content)
        article.update(classification)

    # Step 6: Structured output generation (RSS, JSON, Markdown)
    print("[*] Generating structured outputs...")
    output_dir = os.path.join(os.path.dirname(__file__), '../data/output')
    timestamp = datetime.utcnow().strftime('%Y-%m-%d_%H%M')
    generate_rss_output(articles, output_dir, timestamp)

    logging.info(f"Structured outputs generated at {timestamp}")

    # Step 7: Logging, notifications & alerts (optional, currently logging implemented)
    logging.info("ThreatDigest Hub pipeline completed successfully")
    print(f"[✓] Pipeline execution complete. Processed {len(articles)} articles.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.critical(f"Unhandled exception: {e}", exc_info=True)
        print("[✗] An error occurred, check the log for details.")
