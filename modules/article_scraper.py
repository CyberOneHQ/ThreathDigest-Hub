# ==== Module Imports ====
import logging
import requests
from bs4 import BeautifulSoup
from newspaper import Article

# ==== Article Extractor ====
def extract_article_content(url):
    try:
        # Try using newspaper3k first
        article = Article(url)
        article.download()
        article.parse()

        if article.text.strip():
            return article.text.strip()

        raise ValueError("Newspaper3k returned empty text.")

    except Exception as e:
        logging.warning(f"Newspaper3k failed for {url}: {e}. Trying fallback...")

        try:
            # Fallback to manual scraping
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            paragraphs = soup.find_all("p")
            text = "\n".join(p.get_text() for p in paragraphs)

            if text.strip():
                return text.strip()

            logging.error(f"Fallback also failed: no text found in {url}")
            return ""

        except Exception as fallback_error:
            logging.error(f"Fallback scraping failed for {url}: {fallback_error}")
            return ""
