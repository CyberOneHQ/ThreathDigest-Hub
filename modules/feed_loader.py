# modules/feed_loader.py
import yaml
import logging
from pathlib import Path

def load_feeds_from_files(file_paths):
    feeds = []
    for path in file_paths:
        try:
            with open(path, 'r') as f:
                data = yaml.safe_load(f)
                if isinstance(data, list):
                    feeds.extend(data)
                else:
                    logging.warning(f"{path} does not contain a list of feeds.")
        except Exception as e:
            logging.error(f"Failed to load {path}: {e}")
    return feeds
