import hashlib
import sqlite3
import logging
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / 'data' / 'state' / 'seen_hashes.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS seen_articles (
            hash TEXT PRIMARY KEY,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    return conn

def compute_hash(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def is_duplicate(conn, hash_value):
    c = conn.cursor()
    c.execute('SELECT 1 FROM seen_articles WHERE hash=?', (hash_value,))
    return c.fetchone() is not None

def mark_as_seen(conn, hash_value):
    c = conn.cursor()
    c.execute('INSERT INTO seen_articles(hash) VALUES(?)', (hash_value,))
    conn.commit()

def deduplicate(entries):
    conn = init_db()
    unique_entries = []
    for entry in entries:
        article_hash = compute_hash(entry['link'])  # or use entry['title']
        if is_duplicate(conn, article_hash):
            logging.info(f"Duplicate skipped: {entry['link']}")
            continue
        mark_as_seen(conn, article_hash)
        unique_entries.append(entry)
    conn.close()
    logging.info(f"Deduplicated articles. Unique entries: {len(unique_entries)}")
    return unique_entries
