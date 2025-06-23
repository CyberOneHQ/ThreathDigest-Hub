import os
import logging
import feedparser
import yaml
from pathlib import Path

CONFIG_DIR = Path(__file__).parent.parent / "config"
FEED_FILES = ["feeds_google.yaml", "feeds_bing.yaml", "feeds_native.yaml"]

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')

def load_yaml_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            return data.get('feeds', [])
    except Exception as e:
        logging.error(f"Failed to load {filepath.name}: {e}")
        return []

def validate_feed_url(url):
    try:
        feed = feedparser.parse(url)
        if feed.bozo:
            raise Exception(feed.bozo_exception)
        if not feed.entries:
            logging.warning(f"Feed valid but empty: {url}")
        return True
    except Exception as e:
        logging.error(f"Invalid feed URL: {url} | Error: {e}")
        return False

def validate_all_feeds():
    all_feeds = []
    for fname in FEED_FILES:
        path = CONFIG_DIR / fname
        if not path.exists():
            logging.warning(f"Missing config file: {fname}")
            continue
        feeds = load_yaml_file(path)
        for feed in feeds:
            url = feed.get('url')
            if url:
                result = validate_feed_url(url)
                status = "VALID" if result else "INVALID"
                logging.info(f"[{status}] {url}")
            else:
                logging.warning(f"Missing URL in entry: {feed}")

if __name__ == "__main__":
    logging.info("=== Validating Feed Sources ===")
    validate_all_feeds()
