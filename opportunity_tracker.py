import feedparser
import schedule
import time
import csv
import os
from datetime import datetime

# --- CONFIGURATION ---
RSS_URL = "https://opportunities.creativescotland.com/rss/"
# Add the keywords you are looking for (case-insensitive)
CRITERIA = ["funding", "theatre", "jobs", "marketing", "grant"]
OUTPUT_FILE = "matched_opportunities.csv"

def check_opportunities():
    print(f"[{datetime.now()}] Checking Creative Scotland feed...")
    
    # 1. Parse the RSS Feed
    feed = feedparser.parse(RSS_URL)
    
    matched_items = []
    
    # 2. Filter logic
    for entry in feed.entries:
        # Combine title and summary to search through both
        content_to_search = (entry.title + " " + entry.summary).lower()
        
        # Check if any of our criteria keywords are in the content
        if any(keyword.lower() in content_to_search for keyword in CRITERIA):
            matched_items.append({
                'title': entry.title,
                'link': entry.link,
                'published': entry.published,
                'summary': entry.summary[:200] + "..." # Truncate for CSV
            })

    # 3. Save to CSV if new matches found
    if matched_items:
        save_to_csv(matched_items)
        print(f"Success: Found {len(matched_items)} matches.")
    else:
        print("No matches found today.")

def save_to_csv(items):
    file_exists = os.path.isfile(OUTPUT_FILE)
    
    with open(OUTPUT_FILE, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['title', 'link', 'published', 'summary'])
        
        if not file_exists:
            writer.writeheader()
        
        # To avoid duplicates, you could store seen links in a separate list/DB
        # For simplicity, we just append new findings here
        writer.writerows(items)

# --- SCHEDULER ---
# Run every day at 09:00 AM
schedule.every().day.at("09:00").do(check_opportunities)

if __name__ == "__main__":
    print("Opportunity Bot Started. Monitoring Creative Scotland RSS...")
    # Run once immediately on start for testing
    check_opportunities()
    
    while True:
        schedule.run_pending()
        time.sleep(60) # Wait a minute before checking schedule again
