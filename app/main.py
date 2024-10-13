import os
import sys
import json
import re
from dotenv import load_dotenv
from fetch_content.email_fetcher import get_alerts_from_email
from fetch_content.web_scraper import fetch_web_content
from ai_process.text_generator import generate_text
from send_email.email_sender import send_alert_emails
import logging

logger = logging.getLogger(__name__)

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# Load environment variables
load_dotenv()

def read_prompt_template():
    with open('prompt_template.txt', 'r') as file:
        return file.read()

def add_href_to_website(content, url):
    website_pattern = r'(Website: )(.+)'
    return re.sub(website_pattern, f'\\1<a href="{url}">\\2</a>', content)

def process_alerts(alerts, base_prompt):
    processed_alerts = {}
    for alert in alerts:
        keyword = alert['keyword']
        result = process_alert(alert, base_prompt)
        if result:
            if keyword not in processed_alerts:
                processed_alerts[keyword] = []
            processed_alerts[keyword].append(result)
    return processed_alerts

def process_alert(alert, base_prompt):
    keyword = alert['keyword']
    title = alert['title']
    link = alert['link']
    
    content = fetch_web_content(link, keyword)
    
    if not content:
        print(f"Failed to fetch content for {link}")
        return None
    
    prompt = base_prompt.format(keyword=keyword, title=title, content=content[:500], link=link)
    response = generate_text(prompt)
    
    response_json = json.loads(response)
    ai_generated_text = response_json['choices'][0]['message']['content']
    
    ai_generated_text = add_href_to_website(ai_generated_text, link)

    print(keyword, title, link)

    if ai_generated_text.startswith("No"):
        logger.info(f"Content for {title} is not relevant to {keyword}")
        return None
    
    return {
        'title': title,
        'link': link,
        'summary': ai_generated_text
    }

def main():
    base_prompt = read_prompt_template()
    
    alerts = get_alerts_from_email()
    
    if not alerts:
        print("No alerts found.")
        return
    
    processed_alerts = process_alerts(alerts, base_prompt)
    
    if not processed_alerts:
        print("No alerts were successfully processed.")
        return
    
    sender_email = "get@alertyd.com"
    sender_password = "yR2WtPOffk12OJ6t"
    recipient_email = "hroyhong@gmail.com"
    
    send_alert_emails(processed_alerts, sender_email, sender_password, recipient_email)
    
    print(f"Emails sent to {recipient_email} for {len(processed_alerts)} keywords.")

if __name__ == "__main__":
    main()
