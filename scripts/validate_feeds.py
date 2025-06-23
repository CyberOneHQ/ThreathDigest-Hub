# scripts/validate_feeds.py

import requests
import feedparser
import yaml
import sys
import logging

DEFAULT_CONFIG = "config/threatdigest.yml"
TIMEOUT = 10

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")

def load_yaml_feeds(path):
    try:
        with open(path, "r") as f:
            return yaml.safe_load(f)
    except Exception as e:
        logging.error(f"Failed to load feed config: {e}")
        return []

def validate_feed(url):
    try:
        response = requests.get(url, timeout=TIMEOUT)
        if response.status_code != 200:
            return False, f"HTTP {response.status_code}"
        parsed = feedparser.parse(response.text)
        if not parsed.entries:
            return False, "No entries found"
        return True, f"{len(parsed.entries)} entries"
    except requests.exceptions.Timeout:
        return False, "Timeout"
    except Exception as e:
        return False, str(e)

def validate_feeds(config_path):
    feeds = load_yaml_feeds(config_path)
    if not feeds:
        logging.warning("No feeds to validate.")
        return

    print(f"Validating {len(feeds)} feeds from {config_path}...\n")

    for feed in feeds:
        url = feed.get("url")
        name = feed.get("name", "Unnamed Feed")
        if not url:
            print(f"❌ {name}: Missing URL")
            continue
        ok, message = validate_feed(url)
        if ok:
            print(f"✅ {name}: {url} → {message}")
        else:
            print(f"❌ {name}: {url} → {message}")

if __name__ == "__main__":
    config_file = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_CONFIG
    validate_feeds(config_file)
