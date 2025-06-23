import logging
import hashlib
from pathlib import Path

SEEN_HASHES_FILE = Path(__file__).parent.parent / "state" / "seen_hashes.txt"

def load_seen_hashes():
    if SEEN_HASHES_FILE.exists():
        with open(SEEN_HASHES_FILE, "r") as f:
            return set(line.strip() for line in f)
    return set()

def save_seen_hashes(seen_hashes):
    SEEN_HASHES_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(SEEN_HASHES_FILE, "w") as f:
        f.write("\n".join(seen_hashes))

def deduplicate_articles(articles):
    seen_hashes = load_seen_hashes()
    new_hashes = set()
    unique_articles = []

    for article in articles:
        hash_value = article.get("hash")
        if not hash_value:
            hash_value = hashlib.sha256((article["title"] + article["link"]).encode()).hexdigest()
            article["hash"] = hash_value

        if hash_value not in seen_hashes:
            unique_articles.append(article)
            new_hashes.add(hash_value)
        else:
            logging.info(f"Duplicate skipped: {article['link']}")

    seen_hashes.update(new_hashes)
    save_seen_hashes(seen_hashes)

    logging.info(f"Deduplicated articles. Unique entries: {len(unique_articles)}")
    return unique_articles
