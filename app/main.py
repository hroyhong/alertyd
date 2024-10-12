import os
import sys
import json
import re
from dotenv import load_dotenv
from fetch_content.email_fetcher import get_alerts_from_email
from fetch_content.web_scraper import fetch_web_content
from ai_process.text_generator import generate_text
from send_email.email_sender import send_markdown_email
import logging

logger = logging.getLogger(__name__)

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# Load environment variables
load_dotenv()

def read_prompt_template():
    template_path = os.path.join(project_root, 'prompt_template.txt')
    with open(template_path, 'r') as file:
        return file.read()

def add_href_to_website(content, url):
    # Find the Website line and add the href
    website_pattern = r'(Website: )(.+)'
    return re.sub(website_pattern, f'\\1<a href="{url}">\\2</a>', content)

def process_alert(alert, base_prompt):
    """Process a single alert by fetching content and generating AI text."""
    keyword = alert['keyword']
    title = alert['title']
    link = alert['link']
    
    # Fetch web content
    content = fetch_web_content(link, keyword)
    
    if not content:
        print(f"Failed to fetch content for {link}")
        return None
    
    # Generate AI text
    prompt = base_prompt.format(keyword=keyword, title=title, content=content[:500], link=link)
    response = generate_text(prompt)
    
    # Parse the JSON response
    response_json = json.loads(response)
    
    # Extract the content
    ai_generated_text = response_json['choices'][0]['message']['content']
    
    # Add href to the Website line
    ai_generated_text = add_href_to_website(ai_generated_text, link)

    print(keyword, title, link)

        # Check if the content is relevant
    if ai_generated_text.startswith("No"):
        logger.info(f"Content for {title} is not relevant to {keyword}")
        return None
    
    return {
        'title': title,
        'link': link,
        'content': content,
        'summary': ai_generated_text
    }

def main():
    # Read the prompt template
    base_prompt = read_prompt_template()
    
    # Fetch alerts from email
    alerts = get_alerts_from_email()
    
    if not alerts:
        print("No alerts found.")
        return
    
    processed_alerts = []
    
    for alert in alerts:
        result = process_alert(alert, base_prompt)
        if result:
            processed_alerts.append(result)
    
    if not processed_alerts:
        print("No alerts were successfully processed.")
        return
    
    # Compose email content
    email_content = ""
    for alert in processed_alerts:
        email_content += f"{alert['summary']}\n\n"
        email_content += "---\n\n"
    
    # Send email
    sender_email = "get@alertyd.com"
    sender_password = "yR2WtPOffk12OJ6t"
    recipient_email = "hroyhong@gmail.com"
    subject = "Your Daily Google Alerts Summary"
    
    send_markdown_email(sender_email, sender_password, recipient_email, subject, email_content)
    
    print(f"Email sent to {recipient_email} with {len(processed_alerts)} alerts.")


if __name__ == "__main__":
    main()
