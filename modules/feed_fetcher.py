import feedparser

def fetch_feed_entries():
    feed_urls = [
        "https://news.google.com/rss/search?tbm=nws&q=when:12h+cyber+attack&hl=en-US&gl=US&ceid=US:en"
    ]
    entries = []
    for url in feed_urls:
        feed = feedparser.parse(url)
        entries.extend(feed.entries)
    return [{"title": e.title, "link": e.link} for e in entries]
