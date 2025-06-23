# modules/utils.py

import os
import yaml
import logging
from pathlib import Path

def load_yaml_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f).get('feeds', [])
    except Exception as e:
        logging.error(f"[YAML Error] Failed to load: {filepath} — {e}")
        return []

def ensure_output_directory():
    for folder in ["data/output", "logs", "data/state"]:
        Path(folder).mkdir(parents=True, exist_ok=True)
