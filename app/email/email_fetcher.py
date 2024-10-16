import imaplib
import email
from email.header import decode_header
import os
from dotenv import load_dotenv
import logging
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re


from app.fetch_content.cleaner import clean_link, clean_title


# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Email account credentials
EMAIL = "alertydd@gmail.com"
PASSWORD = "benxskhawtgimywa"

def extract_links_from_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    links = soup.find_all('a')
    alert_links = []
    for link in links:
        href = link.get('href')
        if href and href.startswith('https://www.google.com/url?rct=j&sa=t&url='):
            alert_links.append(href)
    return alert_links

def extract_keyword_from_subject(subject):
    match = re.search(r'Google Alert - (.+)', subject)
    if match:
        return match.group(1).strip()
    return None

def get_alerts_from_email(days=1):
    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    
    try:
        imap.login(EMAIL, PASSWORD)
        logger.info("Successfully logged in")

        imap.select("INBOX")

        date = (datetime.now() - timedelta(days=days)).strftime("%d-%b-%Y")
        search_criteria = f'(FROM "googlealerts-noreply@google.com" SUBJECT "Google Alert -" SINCE "{date}")'
        _, messages = imap.search(None, search_criteria)

        alerts_by_keyword = {}

        for num in messages[0].split():
            _, msg = imap.fetch(num, "(RFC822)")
            for response in msg:
                if isinstance(response, tuple):
                    msg = email.message_from_bytes(response[1])
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding if encoding else "utf-8")
                    
                    subject = clean_title(subject)
                    keyword = extract_keyword_from_subject(subject)
                    if not keyword:
                        continue

                    logger.info(f"Processing email for keyword: {keyword}")

                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == "text/html":
                                body = part.get_payload(decode=True).decode()
                                soup = BeautifulSoup(body, 'html.parser')
                                links = soup.find_all('a')
                                for link in links:
                                    href = link.get('href')
                                    if href and href.startswith('https://www.google.com/url?rct=j&sa=t&url='):
                                        cleaned_link = clean_link(href)  # Use clean_link function
                                        title = link.text.strip()
                                        if keyword not in alerts_by_keyword:
                                            alerts_by_keyword[keyword] = []

                                        alerts_by_keyword[keyword].append({
                                            'link': cleaned_link,
                                            'title': title
                                        })
                                        logger.info(f"Found alert link for '{keyword}': {cleaned_link}")
                                        logger.info(f"Title: {title}")
        return alerts_by_keyword

    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        return []

    finally:
        try:
            imap.close()
            imap.logout()
        except:
            pass

if __name__ == "__main__":
    alerts = get_alerts_from_email()
    logger.info(f"Total alerts found: {len(alerts)}")
    for alert in alerts:
        print(f"Keyword: {alert['keyword']}")
        print(f"Link: {alert['link']}")
        print("---")
