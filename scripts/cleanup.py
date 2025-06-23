import os
import sqlite3
import logging
from datetime import datetime, timedelta
from pathlib import Path

# Setup
BASE_DIR = Path(__file__).parent.parent / "data"
STATE_DB = BASE_DIR / "state" / "seen_hashes.db"
OUTPUT_DIR = BASE_DIR / "output"
RETENTION_DAYS = 365  # Retain 1 year of data

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")

def cleanup_seen_hashes():
    """Delete hash entries older than RETENTION_DAYS from SQLite DB."""
    if not STATE_DB.exists():
        logging.warning("Hash database does not exist.")
        return

    try:
        conn = sqlite3.connect(STATE_DB)
        cursor = conn.cursor()
        cutoff = datetime.utcnow() - timedelta(days=RETENTION_DAYS)
        cursor.execute("DELETE FROM seen_articles WHERE timestamp < ?", (cutoff.isoformat(),))
        deleted = conn.total_changes

        # Compact database to reclaim disk space
        cursor.execute("VACUUM")

        conn.commit()
        conn.close()
        logging.info(f"Deleted {deleted} old hash entries and compacted DB.")
    except Exception as e:
        logging.error(f"Failed to prune hashes: {e}")

def cleanup_old_outputs():
    """Delete files older than RETENTION_DAYS in the output directory."""
    now = datetime.now()
    deleted_count = 0
    for file in OUTPUT_DIR.glob("*"):
        if file.is_file():
            mtime = datetime.fromtimestamp(file.stat().st_mtime)
            if (now - mtime).days > RETENTION_DAYS:
                try:
                    file.unlink()
                    deleted_count += 1
                    logging.info(f"Deleted old file: {file.name}")
                except Exception as e:
                    logging.error(f"Error deleting {file.name}: {e}")
    logging.info(f"Deleted {deleted_count} old output files.")

def main():
    logging.info("=== Running cleanup script ===")
    cleanup_seen_hashes()
    cleanup_old_outputs()
    logging.info("=== Cleanup completed ===")

if __name__ == "__main__":
    main()
