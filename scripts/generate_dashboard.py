import os
import json
from datetime import datetime
from pathlib import Path

# Constants
BASE_DIR = Path(__file__).parent.parent / "data"
AGGREGATED_PATH = BASE_DIR / "aggregated" / "all_cyberattacks.json"
OUTPUT_PATH = BASE_DIR / "output" / "dashboard.md"

def load_entries():
    if AGGREGATED_PATH.exists():
        with open(AGGREGATED_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def generate_markdown(entries):
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write("# 🛡️ ThreatDigest Cyberattack Dashboard\n\n")
        f.write(f"**Last Updated**: `{datetime.utcnow().isoformat()} UTC`\n\n")
        f.write("| Date | Title | Category | Source |\n")
        f.write("|------|-------|----------|--------|\n")

        for entry in entries[:100]:  # Show latest 100
            date = entry.get("published", "")[:10]
            title = entry.get("title", "").replace("|", "").replace("\n", " ").strip()
            link = entry.get("link", "#")
            category = entry.get("classification", {}).get("category", "Unknown")
            source = entry.get("source", "n/a")
            f.write(f"| {date} | [{title}]({link}) | {category} | {source} |\n")

    print(f"[Output] Markdown dashboard generated at: {OUTPUT_PATH}")

def main():
    entries = load_entries()
    if not entries:
        print("No aggregated data found.")
        return
    generate_markdown(entries)

if __name__ == "__main__":
    main()
