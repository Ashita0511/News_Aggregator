from database import push_to_firestore
from intelligence_layer import enrich_dataframe
import feedparser
import pandas as pd
import requests
from datetime import datetime

def fetch_data_engineering_news(rss_url, source_name):
    """
    Fetches and parses an RSS feed using a custom User-Agent to avoid blocks,
    returning a structured Pandas DataFrame with a strict schema.
    """
    print(f"Fetching live feed from: {source_name}...")
    
    # 1. Spoof a standard browser to bypass basic anti-scraping blocks
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    # Enforce strict schema to prevent downstream KeyErrors
    expected_columns = ["Title", "Source", "URL", "Published_Date", "Raw_Content"]
    
    try:
        # 2. Fetch the raw XML with requests instead of feedparser directly
        response = requests.get(rss_url, headers=headers, timeout=10)
        response.raise_for_status() # Raise an exception for HTTP errors (e.g., 404, 403)
        
        # 3. Parse the raw XML string with feedparser
        feed = feedparser.parse(response.content)
        
        articles_data = []
        
        for entry in feed.entries:
            title = entry.get('title', 'No Title')
            link = entry.get('link', '')
            raw_summary = entry.get('summary', 'No summary available.')
            published = entry.get('published', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            
            articles_data.append({
                "Title": title,
                "Source": source_name,
                "URL": link,
                "Published_Date": published,
                "Raw_Content": raw_summary
            })
            
        df = pd.DataFrame(articles_data)
        
        # 4. Handle empty results gracefully
        if df.empty:
            print(f"⚠️ Warning: No entries found for {source_name}. The feed might be empty or blocking the request.")
            df = pd.DataFrame(columns=expected_columns)
            
        return df
        
    except Exception as e:
        print(f"❌ Error fetching from {source_name}: {e}")
        # Return an empty dataframe with the correct schema to keep the pipeline running
        return pd.DataFrame(columns=expected_columns)

# --- TEST THE INGESTION SCRIPT ---
if __name__ == "__main__":
    medium_url = "https://medium.com/feed/tag/data-engineering"
    medium_df = fetch_data_engineering_news(medium_url, "Medium (Data Engineering)")
    
    reddit_url = "https://www.reddit.com/r/dataengineering/.rss"
    reddit_df = fetch_data_engineering_news(reddit_url, "r/dataengineering")
    
    # Combine the dataframes
    final_df = pd.concat([medium_df, reddit_df], ignore_index=True)
    
    print("\n--- Successfully Ingested Articles ---")
    
    # Final safety check before printing
    if not final_df.empty:
        # Pass the raw dataframe to the Intelligence Layer!
        enriched_df = enrich_dataframe(final_df)
        
        push_to_firestore(enriched_df)
    else:
        print("Pipeline execution completed, but no data was extracted from the edge sources.")
