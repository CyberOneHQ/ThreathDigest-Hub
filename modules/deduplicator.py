# ==== Module Imports ====
import os
import logging
import hashlib
from pathlib import Path

# ==== Constants ====
STATE_FILE = Path("state/seen_hashes.txt")

# ==== Ensure State Directory Exists ====
os.makedirs(STATE_FILE.parent, exist_ok=True)

# ==== Functions ====
def load_seen_hashes():
    if not STATE_FILE.exists():
        return set()
    with open(STATE_FILE, "r") as f:
        return set(line.strip() for line in f.readlines())

def save_seen_hashes(seen_hashes):
    with open(STATE_FILE, "w") as f:
        for h in sorted(seen_hashes):
            f.write(f"{h}\n")

def deduplicate_articles(articles):
    seen_hashes = load_seen_hashes()
    updated_hashes = set(seen_hashes)
    unique_articles = []

    for article in articles:
        hash_value = article.get("hash")
        if not hash_value:
            hash_value = hashlib.sha256((article["title"] + article["link"]).encode()).hexdigest()
            article["hash"] = hash_value

        if hash_value not in seen_hashes:
            updated_hashes.add(hash_value)
            unique_articles.append(article)
        else:
            logging.info(f"Duplicate skipped: {article['link']}")

    save_seen_hashes(updated_hashes)
    logging.info(f"Deduplicated articles. Unique entries: {len(unique_articles)}")
    return unique_articles
