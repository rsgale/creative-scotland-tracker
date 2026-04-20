import feedparser
import os
import smtplib
import ssl
from email.message import EmailMessage
from datetime import datetime

# --- CONFIGURATION ---
RSS_URL = "https://opportunities.creativescotland.com/rss/"
# Using "the" for testing - it should match almost everything
CRITERIA = ["funding", "theatre", "marketing", "jobs", "the"] 

def send_email(matches):
    email_user = os.environ.get('EMAIL_USER')
    email_pass = os.environ.get('EMAIL_PASS')
    email_to = os.environ.get('EMAIL_RECIPIENT')

    if not email_user or not email_pass:
        print("Error: Email credentials not found in environment variables.")
        return

    msg = EmailMessage()
    msg['Subject'] = f"Creative Scotland Matches - {datetime.now().strftime('%Y-%m-%d')}"
    msg['From'] = email_user
    msg['To'] = email_to

    body = f"I found {len(matches)} matches today:\n\n"
    for item in matches:
        body += f"TITLE: {item['title']}\nLINK: {item['link']}\n\n"
    
    msg.set_content(body)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_user, email_pass)
        smtp.send_message(msg)

def check_opportunities():
    # FIX 1: Add a User-Agent so the website thinks we are a real browser
    # This prevents the website from blocking the script
    feed = feedparser.parse(RSS_URL, agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
    
    # DEBUG: Print how many items were found in total
    print(f"Total items found in RSS feed: {len(feed.entries)}")
    
    if len(feed.entries) == 0:
        print("Warning: The feed appears to be empty. This usually means the site is blocking the request.")
        return

    matched_items = []
    
    for entry in feed.entries:
        # FIX 2: Check multiple fields (some feeds use 'summary', some 'description')
        title = entry.get('title', '')
        summary = entry.get('summary', entry.get('description', ''))
        
        content_to_search = (title + " " + summary).lower()
        
        if any(keyword.lower() in content_to_search for keyword in CRITERIA):
            matched_items.append({
                'title': title,
                'link': entry.link
            })

    if matched_items:
        print(f"Found {len(matched_items)} matches. Sending email...")
        try:
            send_email(matched_items)
            print("Email sent successfully!")
        except Exception as e:
            print(f"Failed to send email: {e}")
    else:
        print("No matches found today based on your criteria.")

if __name__ == "__main__":
    check_opportunities()
