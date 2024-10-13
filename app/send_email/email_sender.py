import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import markdown
import os
import imaplib
import email
from email.header import decode_header
import logging
import time

logger = logging.getLogger(__name__)

# Feishu email settings
SMTP_SERVER = "smtp.feishu.cn"
SMTP_PORT = 587  # Using STARTTLS
IMAP_SERVER = "imap.feishu.cn"
IMAP_PORT = 993

# Email sending limits
MAX_EMAILS_PER_DAY = 100
MAX_EMAILS_PER_100_SECONDS = 200
email_count = 0
last_email_time = time.time()

def send_markdown_email(sender_email, sender_password, recipient_email, subject, markdown_content):
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject

    html_content = markdown.markdown(markdown_content)
    msg.attach(MIMEText(html_content, 'html'))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        logger.info(f"Email sent: {subject}")
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")

def send_alert_emails(processed_alerts, sender_email, sender_password, recipient_email):
    global email_count, last_email_time
    
    for keyword, alerts in processed_alerts.items():
        if not alerts:
            continue

        subject = f"Get Alertyd for - {keyword}"
        email_content = f"# You are now alerted to '{keyword}'\n\n"
        for alert in alerts:
            email_content += alert['summary'] + "\n\n---\n\n"

        # Check for existing thread
        existing_thread = find_existing_thread(sender_email, sender_password, subject)
        
        # Implement rate limiting
        current_time = time.time()
        if current_time - last_email_time < 100 and email_count >= MAX_EMAILS_PER_100_SECONDS:
            logger.warning("Rate limit reached. Waiting before sending more emails.")
            time.sleep(100 - (current_time - last_email_time))
            email_count = 0
            last_email_time = time.time()
        
        if email_count >= MAX_EMAILS_PER_DAY:
            logger.warning("Daily email limit reached. Stopping email sending.")
            break

        if existing_thread:
            reply_to_thread(sender_email, sender_password, recipient_email, subject, email_content, existing_thread)
        else:
            send_markdown_email(sender_email, sender_password, recipient_email, subject, email_content)
        
        email_count += 1
        last_email_time = time.time()

    logger.info(f"Emails sent for {len(processed_alerts)} keywords.")

def find_existing_thread(sender_email, sender_password, subject):
    try:
        with imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT) as imap:
            imap.login(sender_email, sender_password)
            imap.select('INBOX')
            _, messages = imap.search(None, f'SUBJECT "{subject}"')
            if messages[0]:
                latest_email_id = messages[0].split()[-1]
                _, msg_data = imap.fetch(latest_email_id, "(RFC822)")
                email_body = msg_data[0][1]
                message = email.message_from_bytes(email_body)
                return message["Message-ID"]
    except Exception as e:
        logger.error(f"Error finding existing thread: {str(e)}")
    return None

def reply_to_thread(sender_email, sender_password, recipient_email, subject, content, thread_id):
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = f"Re: {subject}"
    msg['In-Reply-To'] = thread_id
    msg['References'] = thread_id

    html_content = markdown.markdown(content)
    msg.attach(MIMEText(html_content, 'html'))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        logger.info(f"Reply sent: {subject}")
    except Exception as e:
        logger.error(f"Failed to send reply: {str(e)}")

# # Read the generated content from the file
# project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
# generated_content_path = os.path.join(project_root, 'app', 'tests', 'generated_text', 'test.txt')

# with open(generated_content_path, 'r') as file:
#     markdown_content = file.read()

# # Example usage
# sender_email = "get@alertyd.com"
# sender_password = "yR2WtPOffk12OJ6t"  # Your IMAP/SMTP password
# recipient_email = "hroyhong@gmail.com"
# subject = "AI-Generated Article Summary"

# send_markdown_email(sender_email, sender_password, recipient_email, subject, markdown_content)
