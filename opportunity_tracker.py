import feedparser
import os
import requests
import smtplib
import ssl
from email.message import EmailMessage
from datetime import datetime

# --- CONFIGURATION ---
# We use the standard URL that works in browsers
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
    
    # We create a session to store cookies, making us look more human
    session = requests.Session()
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Accept': 'application/rss+xml, application/xml, text/xml, */*',
        'Accept-Language': 'en-GB,en;q=0.9',
        'Referer': 'https://opportunities.creativescotland.com/',
    }
    
    try:
        # Step 1: Visit the homepage first to get a session cookie (very human behavior)
        session.get("https://opportunities.creativescotland.com/", headers=headers, timeout=15)
        
        # Step 2: Get the RSS feed
        response = session.get(RSS_URL, headers=headers, timeout=15)
        
        # Check if we were redirected (e.g., if the URL changed to the homepage)
        if response.url != RSS_URL and not response.url.endswith('/rss/'):
            print(f"Warning: Redirected to {response.url}. The site might be blocking us.")

        # Step 3: Decode using 'utf-8-sig' to remove hidden characters (BOM)
        content = response.content.decode('utf-8-sig')
        
        feed = feedparser.parse(content)
        print(f"Total items found in feed: {len(feed.entries)}")
        
        # If still 0, let's look at the actual text returned
        if len(feed.entries) == 0:
            print("--- DEBUG: SITE RESPONSE START ---")
            print(content[:500])
            print("--- DEBUG: SITE RESPONSE END ---")
            return

        matched_items = []
        for entry in feed.entries:
            title = entry.get('title', 'No Title')
            summary = entry.get('summary', entry.get('description', ''))
            content_to_search = (title + " " + summary).lower()
            
            if any(keyword.lower() in content_to_search for keyword in CRITERIA):
                matched_items.append({'title': title, 'link': entry.get('link', 'No Link')})

        if matched_items:
            print(f"SUCCESS: {len(matched_items)} matches found. Sending email...")
            send_email(matched_items)
        else:
            print("No matches found in the items available.")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    check_opportunities()
