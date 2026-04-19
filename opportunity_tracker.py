import feedparser
import os
import smtplib
from email.message import EmailMessage
from datetime import datetime

# --- CONFIGURATION ---
RSS_URL = "https://opportunities.creativescotland.com/rss/"
CRITERIA = ["funding", "theatre", "marketing", "jobs", "the"] 

def send_email(matches):
    # Get credentials from GitHub Secrets
    email_user = os.environ.get('EMAIL_USER')
    email_pass = os.environ.get('EMAIL_PASS')
    email_to = os.environ.get('EMAIL_RECIPIENT')

    msg = EmailMessage()
    msg['Subject'] = f"Creative Scotland Matches - {datetime.now().strftime('%Y-%m-%d')}"
    msg['From'] = email_user
    msg['To'] = email_to

    # Build the email body
    body = "The following opportunities matched your criteria:\n\n"
    for item in matches:
        body += f"TITLE: {item['title']}\nLINK: {item['link']}\n\n"
    
    msg.set_content(body)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(email_user, email_pass)
        smtp.send_message(msg)

def check_opportunities():
    feed = feedparser.parse(RSS_URL)
    matched_items = []
    
    for entry in feed.entries:
        content_to_search = (entry.title + " " + entry.summary).lower()
        if any(keyword.lower() in content_to_search for keyword in CRITERIA):
            matched_items.append({
                'title': entry.title,
                'link': entry.link
            })

    if matched_items:
        print(f"Found {len(matched_items)} matches. Sending email...")
        send_email(matched_items)
    else:
        print("No matches found today.")

if __name__ == "__main__":
    check_opportunities()
