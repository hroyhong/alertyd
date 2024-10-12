import re
from urllib.parse import urlparse, parse_qs
from typing import Dict

def clean_title(title):
    cleanr = re.compile('<.*?>')
    clean_title = re.sub(cleanr, '', title)
    clean_title = clean_title.replace("<b>", "").replace("</b>", "").replace("&quot;", "")
    return clean_title

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

