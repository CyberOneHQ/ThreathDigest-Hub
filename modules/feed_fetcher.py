import feedparser
import requests
import threading
import hashlib
import logging

# Shared article list and lock
articles = []
lock = threading.Lock()

def fetch_feed(url):
    try:
        parsed = feedparser.parse(url)
        with lock:
            for entry in parsed.entries:
                article_hash = hashlib.sha256((entry.title + entry.link).encode()).hexdigest()
                articles.append({
                    'title': entry.title,
                    'link': entry.link,
                    'published': entry.get('published', ''),
                    'summary': entry.get('summary', ''),
                    'hash': article_hash,
                    'source': url
                })
        logging.info(f"Fetched: {url} with {len(parsed.entries)} entries.")
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
