import os
import yaml
import feedparser
from pathlib import Path

CONFIG_DIR = Path(__file__).parent.parent / "config"
FEED_FILES = ["feeds_google.yaml", "feeds_bing.yaml", "feeds_native.yaml"]

def load_yaml_feeds(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            return data.get('feeds', [])
    except Exception as e:
        print(f"[ERROR] Failed to load {filepath.name}: {e}")
        return []

def validate_feed(url):
    parsed = feedparser.parse(url)
    if not parsed.entries:
        print(f"[WARN] No entries found for: {url}")
        return False
    return True

def main():
    failed = 0
    for filename in FEED_FILES:
        filepath = CONFIG_DIR / filename
        if not filepath.exists():
            print(f"[ERROR] File not found: {filename}")
            failed += 1
            continue

        feeds = load_yaml_feeds(filepath)
        for feed in feeds:
            url = feed.get("url")
            if not url or not validate_feed(url):
                print(f"[FAIL] Unreachable or invalid feed: {url}")
                failed += 1

    if failed > 0:
        print(f"[ERROR] {failed} feed(s) failed validation.")
        exit(1)
    else:
        print("[SUCCESS] All feeds validated.")
        exit(0)

if __name__ == "__main__":
    main()
