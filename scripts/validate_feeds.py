# scripts/validate_feeds.py
import yaml
import logging
import requests
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(levelname)s | %(message)s')

def load_feeds_from_yaml(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f).get("feeds", [])
    except Exception as e:
        logging.error(f"Failed to load {filepath.name}: {e}")
        return []

def validate_feed(url):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200 and "<rss" in response.text.lower():
            logging.info(f"✅ {url}")
        else:
            logging.warning(f"⚠️  {url} returned non-RSS content or bad status")
    except Exception as e:
        logging.error(f"❌ Error fetching {url}: {e}")

def main():
    config_dir = Path("config")
    files = ["feeds_bing.yaml", "feeds_google.yaml", "feeds_native.yaml"]

    for file_name in files:
        logging.info(f"\n--- Validating feeds in {file_name} ---")
        path = config_dir / file_name
        feeds = load_feeds_from_yaml(path)
        if not feeds:
            logging.warning(f"No feeds loaded from {file_name}")
            continue
        for feed in feeds:
            validate_feed(feed["url"])

if __name__ == "__main__":
    main()
