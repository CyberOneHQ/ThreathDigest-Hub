# ==== Module Imports ====
import logging
from urllib.parse import urlparse, parse_qs
from newspaper import Article
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# ==== Logging Setup ====
logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO
)

# ==== HTTP Session with Retry Strategy ====
session = requests.Session()
retry_strategy = Retry(
    total=2,
    backoff_factor=0.5,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET", "HEAD"]
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("https://", adapter)
session.mount("http://", adapter)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
}

# ==== Resolve Final Destination for Redirect URLs ====
def resolve_original_url(url):
    if any(p in url for p in ["news.google.com", "bing.com/news/apiclick", "facebook.com/l.php", "t.co"]):
        parsed = urlparse(url)
        query_params = parse_qs(parsed.query)
        if 'url' in query_params:
            return query_params['url'][0]
        try:
            response = session.head(url, allow_redirects=True, timeout=5, headers=HEADERS)
            return response.url
        except Exception as e:
            logging.warning(f"Redirect resolution failed for {url}: {e}")
            return url
    return url

# ==== Primary Scraper Using newspaper3k ====
def extract_with_newspaper(url):
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.text.strip()
    except Exception as e:
        logging.warning(f"Newspaper3k failed for {url}: {e}")
        return None

# ==== Fallback Scraper Using BeautifulSoup ====
def extract_with_fallback(url):
    try:
        response = session.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        paragraphs = soup.find_all('p')
        content = ' '.join(p.get_text() for p in paragraphs)
        return content.strip() if content else None
    except Exception as e:
        logging.error(f"Fallback scraping failed for {url}: {e}")
        return None

# ==== Unified Content Extraction ====
def extract_article_content(raw_url):
    clean_url = resolve_original_url(raw_url)
    logging.info(f"Processing: {clean_url}")

    content = extract_with_newspaper(clean_url)
    if content:
        logging.info(f"Extracted {len(content)} chars using newspaper3k")
        return clean_url, content

    content = extract_with_fallback(clean_url)
    if content:
        logging.info(f"Extracted {len(content)} chars using fallback parser")
        return clean_url, content

    logging.warning(f"No content extracted from {clean_url}")
    return clean_url, None

# ==== Parallel Execution ====
def process_urls_in_parallel(url_list, max_threads=8):
    results = {}
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        future_to_url = {executor.submit(extract_article_content, url): url for url in url_list}
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                clean_url, content = future.result()
                results[clean_url] = content
            except Exception as exc:
                logging.error(f"Exception while processing {url}: {exc}")
    return results
