from feedgen.feed import FeedGenerator
import os

def generate_rss_output(entries):
    fg = FeedGenerator()
    fg.id("https://yourdomain.com/threatdigest")
    fg.title("ThreatDigest Hub - Curated Cyber Incidents")
    fg.link(href="https://yourdomain.com", rel="self")
    fg.language("en")

    for entry in entries:
        fe = fg.add_entry()
        fe.title(entry['title'])
        fe.link(href=entry['link'])

    output_file = os.path.join("data", "output", "rss_cyberattacks.xml")
    fg.rss_file(output_file)
    print(f"[Output] RSS feed saved to {output_file}")
