from feedgen.feed import FeedGenerator
import os

def write_feeds(entries):
    fg = FeedGenerator()
    fg.id("https://yourdomain.com/cyberattacks")
    fg.title("ThreatDigest Hub - Likely Cyber Incidents")
    fg.link(href="https://yourdomain.com", rel="self")
    fg.language("en")

    for entry in entries:
        fe = fg.add_entry()
        fe.title(entry['title'])
        fe.link(href=entry['link'])

    output_path = os.path.join("data", "outputs", "cyberattacks_news.xml")
    fg.rss_file(output_path)
    print(f"[FeedWriter] Written {len(entries)} entries to {output_path}")
