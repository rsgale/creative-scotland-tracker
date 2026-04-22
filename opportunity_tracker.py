import feedparser
import os
import requests
import smtplib
import ssl
from email.message import EmailMessage
from datetime import datetime

# --- CONFIGURATION ---
RSS_URL = "https://opportunities.creativescotland.com/api/rss/"
# Remember to remove "the" once you are happy with the results!
CRITERIA = ["funding", "theatre", "marketing", "jobs", "write"] 

def send_email(matches):
    email_user = os.environ.get('EMAIL_USER')
    email_pass = os.environ.get('EMAIL_PASS')
    email_to = os.environ.get('EMAIL_RECIPIENT')

    msg = EmailMessage()
    msg['Subject'] = f"✨ Creative Scotland matches: {len(matches)} found ({datetime.now().strftime('%d %b')})"
    msg['From'] = email_user
    msg['To'] = email_to

    # Build a much nicer email body
    body = f"Hello,\n\nI found {len(matches)} new opportunities matching your criteria today.\n"
    body += "="*60 + "\n\n"

    for item in matches:
        body += f"TITLE:     {item['title']}\n"
        body += f"DATE:      {item['published']}\n"
        body += f"LINK:      {item['link']}\n"
        body += f"SUMMARY:   {item['summary']}\n"
        body += "\n" + "-"*40 + "\n\n"

    body += "This is an automated check from your GitHub Opportunity Tracker."
    
    msg.set_content(body)
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_user, email_pass)
        smtp.send_message(msg)

def check_opportunities():
    print(f"--- Starting Check: {datetime.now()} ---")
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        response = requests.get(RSS_URL, headers=headers, timeout=20)
        response.raise_for_status()
        feed = feedparser.parse(response.content)
        print(f"Total items found in feed: {len(feed.entries)}")
        
        matched_items = []
        for entry in feed.entries:
            title = entry.get('title', '')
            # Pulling the summary and cleaning it up a bit
            summary = entry.get('summary', entry.get('description', 'No description available.'))
            # Some RSS summaries are very long; this limits it to 300 characters
            summary_snippet = (summary[:300] + '...') if len(summary) > 300 else summary
            
            published = entry.get('published', 'No date listed')
            
            content_to_search = (title + " " + summary).lower()
            
            if any(keyword.lower() in content_to_search for keyword in CRITERIA):
                matched_items.append({
                    'title': title,
                    'link': entry.get('link', 'No Link'),
                    'published': published,
                    'summary': summary_snippet
                })

        if matched_items:
            print(f"SUCCESS: {len(matched_items)} matches found. Sending email...")
            send_email(matched_items)
        else:
            print("No matches found.")

    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    check_opportunities()
