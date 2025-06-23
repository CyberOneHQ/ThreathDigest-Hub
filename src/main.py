from fetch_feeds import get_feeds
from scraper import fetch_article_text
from classifier import classify_incident
from feed_writer import write_feeds

def main():
    print("[*] Starting ThreatDigest Hub")
    entries = get_feeds()
    enriched_entries = []

    for entry in entries:
        content = fetch_article_text(entry['link'])
        if not content:
            continue
        classification = classify_incident(content)
        entry.update(classification)
        enriched_entries.append(entry)

    write_feeds(enriched_entries)
    print(f"[+] Completed. Entries processed: {len(enriched_entries)}")

if __name__ == "__main__":
    main()
