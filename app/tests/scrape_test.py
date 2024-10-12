import sys
import os

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from app.fetch_content.web_scraper import fetch_web_content

def test_fetch_web_content():
    url = "https://www.youtube.com/watch?v=1bUy-1hGZpI&t=197s"
    content = fetch_web_content(url)
    print(content)
    return content

if __name__ == "__main__":
    content = test_fetch_web_content()
    # Ensure the directory exists
    os.makedirs('scrape_tests', exist_ok=True)
    # Write the content to a file
    with open('app/tests/scrape_tests/test.txt', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Content has been written to scrape_tests/test.txt")

