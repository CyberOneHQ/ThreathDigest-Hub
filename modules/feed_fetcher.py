import os
import yaml
import logging
from pathlib import Path

CONFIG_DIR = Path(__file__).parent.parent / "config"
FEED_FILES = ["feeds_google.yaml", "feeds_bing.yaml", "feeds_native.yaml"]

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')

def load_yaml_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            logging.info(f"Loaded {filepath.name} successfully.")
            return data.get('feeds', [])
    except Exception as e:
        logging.error(f"Error loading YAML file {filepath.name}: {e}")
        return []

def load_all_feeds():
    all_feeds = []
    for feed_file in FEED_FILES:
        filepath = CONFIG_DIR / feed_file
        if filepath.exists():
            feeds = load_yaml_file(filepath)
            all_feeds.extend(feeds)
        else:
            logging.warning(f"Feed config file not found: {filepath}")
    logging.info(f"Total feeds loaded: {len(all_feeds)}")
    return all_feeds

if __name__ == "__main__":
    feeds = load_all_feeds()
    print(f"Feeds loaded: {len(feeds)}")
    for feed in feeds:
        print(feed)
