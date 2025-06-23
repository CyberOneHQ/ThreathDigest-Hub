import feedparser

def get_feeds():
    # TODO: Load config dynamically
    feeds = [
        "https://news.google.com/rss/search?tbm=nws&q=when:12h+cyber+attack&hl=en-US&gl=US&ceid=US:en"
    ]
    entries = []
    for url in feeds:
        feed = feedparser.parse(url)
        entries.extend(feed.entries)
    return [{"title": e.title, "link": e.link} for e in entries]
