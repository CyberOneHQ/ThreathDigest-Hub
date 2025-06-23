import logging
import hashlib

def deduplicate_articles(articles):
    seen_hashes = set()
    unique_articles = []
    
    for article in articles:
        hash_value = article.get("hash")
        if not hash_value:
            hash_value = hashlib.sha256((article["title"] + article["link"]).encode()).hexdigest()
            article["hash"] = hash_value

        if hash_value not in seen_hashes:
            seen_hashes.add(hash_value)
            unique_articles.append(article)
        else:
            logging.info(f"Duplicate skipped: {article['link']}")

    logging.info(f"Deduplicated articles. Unique entries: {len(unique_articles)}")
    return unique_articles
