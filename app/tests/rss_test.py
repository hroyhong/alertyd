import sys
import os

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from app.fetch_content.rss_parser import fetch_rss_content

def test_fetch_rss_content():
    RSS_content = fetch_rss_content(os.getenv("RSS_URL_TEST"))
    print(RSS_content)

if __name__ == "__main__":
    test_fetch_rss_content()