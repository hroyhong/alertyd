import feedparser
from typing import List, Dict, Union
import logging
from urllib.parse import urlparse, parse_qs
import re
from .cleaner import clean_article

logger = logging.getLogger(__name__)

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

    cleaned_entries = [clean_article(article) for article in all_articles]

    return cleaned_entries
