import os
import sys
import random
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.utils import ChromeType
import time
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse
import zipfile
import stat
import jmespath
from selenium.webdriver.common.by import By

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

# User-Agent strings for rotating in requests
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
]

# Add a simple cache
content_cache = {}

def get_domain(url):
    return urlparse(url).netloc

def fetch_web_content(url, keyword):
    domain = get_domain(url)
    
    # Check if content is already in cache
    if url in content_cache:
        print(f"Returning cached content for {url}")
        return content_cache[url]

    content = None

    if 'youtube.com' in domain or 'youtu.be' in domain:
        print("Fetching YouTube transcript.")
        content = fetch_youtube_transcript(url)
    elif 'twitter.com' in domain or '.x.com' in domain:
        print("Fetching Twitter content.")
        content = fetch_twitter_content(url)
    elif 'reddit.com' in domain:
        print("Fetching Reddit content.")
        content = scrape_reddit(url)
    else:
        print(f"Fetching general web content for {domain}")
        content = fetch_general_web_content(url)

    if content:
        content_cache[url] = content

    if keyword not in content:
        return None
    
    return content

def fetch_twitter_content(url):
    _xhr_calls = []

    def intercept_response(response):
        if response.request.resource_type == "xhr":
            _xhr_calls.append(response)
        return response

    options = Options()
    options.headless = True
    options.add_argument(f"user-agent={random.choice(user_agents)}")
    options.add_argument("--disable-blink-features=AutomationControlled")
    
    driver_path = download_chromedriver()
    driver = webdriver.Chrome(executable_path=driver_path, options=options)

    try:
        driver.get(url)
        driver.execute_cdp_cmd('Network.enable', {})
        driver.execute_cdp_cmd('Network.setRequestInterception', {'patterns': [{'urlPattern': '*'}]})
        driver.on('Network.responseReceived', lambda params: intercept_response(params['response']))

        driver.implicitly_wait(10)
        driver.find_element(By.CSS_SELECTOR, "[data-testid='tweet']")

        tweet_calls = [f for f in _xhr_calls if "TweetResultByRestId" in f.url]
        for xhr in tweet_calls:
            data = xhr.json()
            tweet_data = data['data']['tweetResult']['result']
            return parse_tweet(tweet_data)

    except Exception as e:
        print(f"Error fetching Twitter content: {e}")
        return None

    finally:
        driver.quit()

def fetch_general_web_content(url):
    content = fetch_web_content_with_requests(url)
    if not content:
        content = fetch_web_content_with_selenium(url)
    return content

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

        # # Special handling for Twitter
        # if 'twitter.com' in url:
        #     tweet_text = soup.find('div', {'data-testid': 'tweetText'})
        #     return tweet_text.get_text(separator="\n", strip=True) if tweet_text else None

        # General website content extraction
        content_set = set()  # Use a set to avoid duplicates
        for tag in ['article', 'main', 'section', 'div']:
            for class_name in ['content', 'main', 'article', 'post', 'entry']:
                elements = soup.find_all(tag, {'class': lambda x: x and class_name in x})
                for elem in elements:
                    content_set.add(elem.get_text(separator="\n", strip=True))
        
        web_content = "\n\n".join(content_set)  # Join unique content pieces
        return web_content if web_content else None

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
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    try:
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
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
        if 'driver' in locals():
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

def download_chromedriver(version="114.0.5735.90"):
    base_url = f"https://chromedriver.storage.googleapis.com/{version}/"
    file_name = "chromedriver_mac64.zip"  # Adjust this if you're using a different OS
    download_url = base_url + file_name

    # Create a directory for ChromeDriver if it doesn't exist
    os.makedirs("chromedriver", exist_ok=True)

    # Download the ZIP file
    response = requests.get(download_url)
    zip_path = os.path.join("chromedriver", file_name)
    with open(zip_path, "wb") as f:
        f.write(response.content)

    # Extract the ZIP file
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall("chromedriver")

    # Set executable permissions
    chromedriver_path = os.path.abspath(os.path.join("chromedriver", "chromedriver"))
    st = os.stat(chromedriver_path)
    os.chmod(chromedriver_path, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    return chromedriver_path

def parse_tweet(data):
    result = jmespath.search(
        """{
        created_at: legacy.created_at,
        text: legacy.full_text,
        favorite_count: legacy.favorite_count,
        retweet_count: legacy.retweet_count,
        reply_count: legacy.reply_count,
        quote_count: legacy.quote_count,
        language: legacy.lang,
        user_id: legacy.user_id_str,
        id: legacy.id_str,
        conversation_id: legacy.conversation_id_str,
        views: views.count
    }""",
        data,
    )
    return result