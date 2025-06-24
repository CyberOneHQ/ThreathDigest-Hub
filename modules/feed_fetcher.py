# ==== Module Imports ====
import feedparser
import requests
import threading
import hashlib
import logging

# ==== Local Module ====
from modules.article_scraper import resolve_original_url  # Ensure imported

# ==== Shared State ====
articles = []
lock = threading.Lock()

# ==== Feed Fetching Logic ====
def fetch_feed(url):
    try:
        parsed = feedparser.parse(url)
        local_articles = []

        for entry in parsed.entries:
            clean_link = resolve_original_url(entry.link)  # Resolve redirect early

            article_hash = hashlib.sha256((entry.title + clean_link).encode()).hexdigest()
            local_articles.append({
                'title': entry.title,
                'link': clean_link,
                'published': entry.get('published', ''),
                'summary': entry.get('summary', ''),
                'hash': article_hash,
                'source': url
            })

        with lock:
            articles.extend(local_articles)

        logging.info(f"Fetched {len(local_articles)} articles from {url}")

    except Exception as e:
        logging.error(f"Error fetching {url}: {e}")

def fetch_articles_multithreaded(feeds_config):
    threads = []
    for feed in feeds_config:
        t = threading.Thread(target=fetch_feed, args=(feed['url'],))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    return articles

def fetch_articles(feeds_config):
    global articles
    articles = []
    return fetch_articles_multithreaded(feeds_config)
