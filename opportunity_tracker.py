import feedparser
import os
import requests
import smtplib
import ssl
from email.message import EmailMessage
from datetime import datetime

# --- CONFIGURATION ---
RSS_URL = "https://opportunities.creativescotland.com/rss/"
CRITERIA = ["funding", "theatre", "marketing", "jobs", "the"] 

def send_email(matches):
    email_user = os.environ.get('EMAIL_USER')
    email_pass = os.environ.get('EMAIL_PASS')
    email_to = os.environ.get('EMAIL_RECIPIENT')

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
    print(f"--- Starting Check: {datetime.now()} ---")
    
    # Use 'requests' to bypass bot-blocking
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        response = requests.get(RSS_URL, headers=headers, timeout=20)
        response.raise_for_status() # Check if the website blocked us (e.g. 403 error)
        print("Successfully fetched the RSS feed data.")
    except Exception as e:
        print(f"FAILED to reach the website: {e}")
        return

    # Parse the downloaded text
    feed = feedparser.parse(response.text)
    print(f"Total items found in feed: {len(feed.entries)}")
    
    matched_items = []
    
    for entry in feed.entries:
        title = entry.get('title', 'No Title')
        # Check both summary and description
        summary = entry.get('summary', entry.get('description', ''))
        
        content_to_search = (title + " " + summary).lower()
        
        # DEBUG: Print titles as we check them
        print(f"Checking item: {title}")
        
        if any(keyword.lower() in content_to_search for keyword in CRITERIA):
            matched_items.append({
                'title': title,
                'link': entry.get('link', 'No Link')
            })

    if matched_items:
        print(f"MATCHES FOUND: {len(matched_items)}. Sending email...")
        send_email(matched_items)
        print("Email process complete.")
    else:
        print("No matches found in the items listed above.")

if __name__ == "__main__":
    check_opportunities()
