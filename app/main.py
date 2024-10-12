import os
from dotenv import load_dotenv
from email.email_sender import send_markdown_email
from fetch_content.web_scraper import fetch_web_content
from fetch_content.rss_parser import fetch_rss_content

load_dotenv()

