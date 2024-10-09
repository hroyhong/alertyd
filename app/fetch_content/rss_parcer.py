import feedparser
from typing import List, Dict, Union
import logging
from urllib.parse import urlparse, parse_qs
import re

logger = logging.getLogger(__name__)
# Function to clean HTML from titles
def clean_title(title):
    cleanr = re.compile('<.*?>')
    clean_title = re.sub(cleanr, '', title)
    clean_title = clean_title.replace("<b>", "").replace("</b>", "").replace("&quot;", "")
    return clean_title

# Function to clean Google redirect links
def clean_link(url):
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    return query_params['url'][0] if 'url' in query_params else url


def clean_article(article: Dict) -> Dict:
    """
    Clean all fields of an article.

    Args:
    article (Dict): A dictionary containing article information.

    Returns:
    Dict: The cleaned article dictionary.
    """
    cleaned_article = {
        'title': clean_title(article['title']),
        'published': article['published'],
        'link': clean_link(article['link']),
    }
    return cleaned_article


def fetch_rss_content(rss_urls: Union[str, List[str]]) -> List[Dict]:
    """
    Fetch content from one or multiple RSS feeds.

    Args:
    rss_urls (Union[str, List[str]]): A single RSS feed URL or a list of RSS feed URLs to fetch content from.

    Returns:
    List[Dict]: A list of dictionaries, each containing information about an article.
    """
    all_articles = []

    # Convert single URL to a list if necessary
    if isinstance(rss_urls, str):
        rss_urls = [rss_urls]

    for rss_url in rss_urls:
        try:
            logger.info(f"Fetching content from {rss_url}")
            feed = feedparser.parse(rss_url)
            for entry in feed.entries:
                article = {
                    'title': entry.title,
                    'link': entry.link,
                    'published': entry.published if hasattr(entry, 'published') else 'No date available',
                }
                all_articles.append(article)
        except Exception as e:
            logger.error(f"An error occurred while parsing {rss_url}: {e}")

    return [clean_article(article) for article in all_articles]
