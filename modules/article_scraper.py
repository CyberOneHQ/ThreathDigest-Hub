from newspaper import Article

def extract_full_text(url):
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.text
    except Exception as e:
        print(f"[Scraper Error] {url} - {e}")
        return None
