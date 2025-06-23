import os
import json
from datetime import datetime
from pathlib import Path
from feedgen.feed import FeedGenerator

BASE_DIR = Path(__file__).parent.parent / "data"
AGGREGATED_FILE = BASE_DIR / "aggregated" / "all_cyberattacks.json"
OUTPUT_DIR = BASE_DIR / "output"
RSS_FILE = OUTPUT_DIR / "rss_cyberattacks.xml"
DASHBOARD_FILE = OUTPUT_DIR / "dashboard.md"

def load_aggregated():
    if AGGREGATED_FILE.exists():
        with open(AGGREGATED_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def generate_rss(entries):
    fg = FeedGenerator()
    fg.id("https://cyberonehq.com/threatdigest")
    fg.title("ThreatDigest Hub - Latest Cyberattacks")
    fg.link(href="https://cyberonehq.com", rel="alternate")
    fg.language("en")

    for entry in entries[:50]:  # Limit to most recent 50
        fe = fg.add_entry()
        fe.id(entry["hash"])
        fe.title(entry["title"])
        fe.link(href=entry["link"])
        fe.published(entry.get("published", datetime.utcnow().isoformat()))
        fe.description(f"{entry.get('classification', {}).get('category', '')} | Source: {entry.get('source', '')}")

    fg.rss_file(str(RSS_FILE))
    print(f"[Output] RSS generated at {RSS_FILE}")

def generate_dashboard_md(entries):
    with open(DASHBOARD_FILE, 'w', encoding='utf-8') as f:
        f.write("# 🛡️ ThreatDigest Cyberattack Feed\n\n")
        f.write(f"Updated: {datetime.utcnow().isoformat()} UTC\n\n")
        f.write("| Date | Title | Category | Source |\n")
        f.write("|------|-------|----------|--------|\n")
        for entry in entries[:100]:  # Show 100 latest
            date = entry.get("published", "")[:10]
            title = entry.get("title", "").replace("|", "")
            link = entry.get("link", "#")
            category = entry.get("classification", {}).get("category", "Unknown")
            source = entry.get("source", "n/a")
            f.write(f"| {date} | [{title}]({link}) | {category} | {source} |\n")
    print(f"[Output] Markdown dashboard saved to {DASHBOARD_FILE}")

def main():
    entries = load_aggregated()
    if not entries:
        print("No entries found for output.")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    generate_rss(entries)
    generate_dashboard_md(entries)

if __name__ == "__main__":
    main()
