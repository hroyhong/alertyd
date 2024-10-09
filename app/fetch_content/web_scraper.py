import os
import sys
import random
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

# User-Agent strings for rotating in requests
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
]

# Function to fetch web content using requests and BeautifulSoup
def fetch_web_content_with_requests(url):
    headers = {
        "User-Agent": random.choice(user_agents),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://www.google.com/",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Special handling for Twitter
        if 'twitter.com' in url:
            tweet_text = soup.find('div', {'data-testid': 'tweetText'})
            return tweet_text.get_text(separator="\n", strip=True) if tweet_text else None

        # General website content extraction
        web_content = ""
        for tag in ['article', 'main', 'section', 'div']:
            for class_name in ['content', 'main', 'article', 'post', 'entry']:
                elements = soup.find_all(tag, {'class': lambda x: x and class_name in x})
                for elem in elements:
                    web_content += elem.get_text(separator="\n", strip=True) + "\n"
        return web_content.strip() if web_content else None

    except requests.exceptions.RequestException as e:
        print(f"Error fetching web content with requests: {e}")
        return None

def scrape_reddit(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to retrieve Reddit page: {response.status_code}")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')
    post_content = soup.find('div', class_='Post')
    if post_content:
        return post_content.get_text(separator="\n", strip=True)
    return None

# Function to fetch web content using Selenium
def fetch_web_content_with_selenium(url):
    options = Options()
    options.headless = True
    options.add_argument(f"user-agent={random.choice(user_agents)}")
    options.add_argument("--disable-blink-features=AutomationControlled")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get(url)
        time.sleep(5)

        # Special handling for Twitter
        if 'twitter.com' in url:
            tweet_text_elements = driver.find_elements(By.XPATH, "//div[@data-testid='tweetText']")
            tweet_text = "\n".join([element.text for element in tweet_text_elements if element.text.strip()])
            return tweet_text

        # Special handling for Reddit
        if 'reddit.com' in url:
            return scrape_reddit(url)

        # General website content extraction
        web_content = ""
        for tag in ['article', 'main', 'section', 'div']:
            for class_name in ['content', 'main', 'article', 'post', 'entry']:
                elements = driver.find_elements(By.XPATH, f"//{tag}[contains(@class, '{class_name}')]")
                for elem in elements:
                    web_content += elem.text + "\n"
        return web_content.strip()

    except Exception as e:
        print(f"Error fetching web content with Selenium: {e}")
        return None

    finally:
        driver.quit()

def fetch_youtube_transcript(url):
    try:
        # Extract video ID from the URL
        video_id = url.split('v=')[1].split('&')[0]
        
        # Fetch the transcript
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        
        # Combine all text entries into a single string
        full_transcript = ' '.join([entry['text'] for entry in transcript])
        
        return full_transcript
    except Exception as e:
        print(f"Error fetching YouTube transcript: {e}")
        return None
# Function to fetch web content using requests first, then falling back to Selenium if needed
def fetch_web_content(url):
    if 'youtube.com' in url or 'youtu.be' in url:
        print("Fetching YouTube transcript.")
        return fetch_youtube_transcript(url)

    web_content = fetch_web_content_with_requests(url)
    if web_content:
        return web_content

    web_content = fetch_web_content_with_selenium(url)
    if web_content:
        return web_content

    return None

