# ==== Module Imports ====
import os
import logging
import hashlib
from pathlib import Path

# ==== State File Path ====
SEEN_HASHES_FILE = Path(__file__).parent.parent / "state" / "seen_hashes.txt"

# ==== Load Seen Hashes ====
def load_seen_hashes():
    if not SEEN_HASHES_FILE.exists():
        return set()
    with open(SEEN_HASHES_FILE, "r") as f:
        return set(line.strip() for line in f.readlines())

# ==== Save Seen Hashes ====
def save_seen_hashes(hashes):
    SEEN_HASHES_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(SEEN_HASHES_FILE, "w") as f:
        for h in sorted(hashes):
            f.write(f"{h}\n")

# ==== Deduplication Logic ====
def deduplicate_articles(articles):
    seen_hashes = load_seen_hashes()
    new_hashes = set()
    unique_articles = []

    for article in articles:
        raw_hash = article.get("hash")
        if not raw_hash:
            raw_hash = hashlib.sha256((article["title"] + article["link"]).encode()).hexdigest()
            article["hash"] = raw_hash

        if raw_hash not in seen_hashes:
            unique_articles.append(article)
            new_hashes.add(raw_hash)
        else:
            logging.info(f"Duplicate skipped: {article['link']}")

    total_seen = seen_hashes.union(new_hashes)
    save_seen_hashes(total_seen)

    logging.info(f"Deduplicated articles. Unique entries: {len(unique_articles)}")
    return unique_articles
