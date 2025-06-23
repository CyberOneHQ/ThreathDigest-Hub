from modules.feed_fetcher import fetch_feed_entries
from modules.article_scraper import extract_full_text
from modules.ai_classifier import classify_article
from modules.feed_writer import generate_rss_output

def main():
    print("[+] Running ThreatDigest Hub pipeline")
    entries = fetch_feed_entries()
    enriched = []

    for entry in entries:
        article = extract_full_text(entry['link'])
        if not article:
            continue
        metadata = classify_article(article)
        entry.update(metadata)
        enriched.append(entry)

    generate_rss_output(enriched)
    print(f"[✓] Completed. Processed {len(enriched)} articles.")

if __name__ == "__main__":
    main()
