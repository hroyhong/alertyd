import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import markdown
import os

def send_markdown_email(sender_email, sender_password, recipient_email, subject, markdown_content):
    # Convert Markdown to HTML
    html_content = markdown.markdown(markdown_content)

    # Create the email message
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = recipient_email

    # Attach both plain text and HTML versions
    text_part = MIMEText(markdown_content, 'plain')
    html_part = MIMEText(html_content, 'html')
    msg.attach(text_part)
    msg.attach(html_part)

    # Send the email
    try:
        with smtplib.SMTP('smtp.feishu.cn', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        print("Email sent successfully")
    except Exception as e:
        print(f"Error sending email: {e}")

# Read the generated content from the file
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
generated_content_path = os.path.join(project_root, 'app', 'tests', 'generated_text', 'test.txt')

with open(generated_content_path, 'r') as file:
    markdown_content = file.read()

# Example usage
sender_email = "get@alertyd.com"
sender_password = "yR2WtPOffk12OJ6t"  # Your IMAP/SMTP password
recipient_email = "hroyhong@gmail.com"
subject = "AI-Generated Article Summary"

send_markdown_email(sender_email, sender_password, recipient_email, subject, markdown_content)
