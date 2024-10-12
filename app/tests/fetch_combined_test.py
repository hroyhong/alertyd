import os
import sys

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from app.fetch_content.rss_parser import fetch_rss_content
from app.fetch_content.web_scraper import fetch_web_content

def test_fetch_combined_content():
    rss_content = fetch_rss_content(os.getenv("RSS_URL_TEST"))
    
    # Ensure rss_content is not empty and is a list
    if not rss_content or not isinstance(rss_content, list):
        print("RSS content is empty or not a list")
        return []

    # Take the first 4 items or less if there are fewer than 4
    items_to_process = rss_content[:4]
    
    results = []
    for item in items_to_process:
        try:
            # Ensure each item has 'title' and 'link' keys
            if 'title' not in item or 'link' not in item:
                print(f"Skipping item: missing 'title' or 'link' key")
                continue

            title = item['title']
            link = item['link']
            print(f"\nProcessing: {title}")
            print(f"URL: {link}")

            web_content = fetch_web_content(link)
            
            if web_content:
                results.append({
                    'title': title,
                    'content': web_content,
                    'link': link
                })
                print("Content fetched successfully")
                print(f"Content preview: {web_content[:200]}...")
            else:
                print("No content fetched")

        except Exception as e:
            print(f"Error processing item: {e}")
            continue

        print("-" * 50)
    
    return results

def get_first_fetched_content():
    fetched_content = test_fetch_combined_content()
    if fetched_content:
        return {
            'title': fetched_content[0]['title'],
            'content': fetched_content[0]['content'],
            'link': fetched_content[0]['link']
        }
    return None

if __name__ == "__main__":
    fetched_content = test_fetch_combined_content()
    print(f"\nFetched {len(fetched_content)} items successfully")
    for item in fetched_content:
        print(f"Title: {item['title']}")
        print(f"Content length: {len(item['content'])}")
        print("-" * 30)