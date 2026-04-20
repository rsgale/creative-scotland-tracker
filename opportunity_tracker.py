import feedparser
import os
import requests
import smtplib
import ssl
from email.message import EmailMessage
from datetime import datetime

# --- CONFIGURATION ---
# We will try these in order until one works
RSS_URLS = [
    "https://opportunities.creativescotland.com/rss",         # No trailing slash
    "https://opportunities.creativescotland.com/rss/latest",  # Common alternative
    "https://opportunities.creativescotland.com/rss/"         # Original with slash
]
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
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }
    
    working_feed = None
    
    # Try the different URL variations
    for url in RSS_URLS:
        print(f"Trying URL: {url}")
        try:
            response = requests.get(url, headers=headers, timeout=20)
            if response.status_code == 200:
                # If we get a 200 (Success), parse it to see if it actually has items
                feed = feedparser.parse(response.content)
                if len(feed.entries) > 0:
                    print(f"SUCCESS: Found working feed at {url}")
                    working_feed = feed
                    break
                else:
                    print(f"URL {url} returned 200 but no entries found.")
            else:
                print(f"URL {url} failed with status code: {response.status_code}")
        except Exception as e:
            print(f"Error trying {url}: {e}")

    if not working_feed:
        print("CRITICAL ERROR: Could not find a working RSS feed URL.")
        return

    matched_items = []
    for entry in working_feed.entries:
        title = entry.get('title', 'No Title')
        summary = entry.get('summary', entry.get('description', ''))
        content_to_search = (title + " " + summary).lower()
        
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
        print("No matches found in the feed today.")

if __name__ == "__main__":
    check_opportunities()
