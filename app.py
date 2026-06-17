import streamlit as st
import pandas as pd
from streamlit_autorefresh import st_autorefresh
import firebase_admin
from firebase_admin import credentials, firestore
import time

# --- 1. FIREBASE INITIALIZATION ---
# Streamlit hot-reloads the script on every update. 
# We must check if Firebase is already initialized to prevent a crash.
if not firebase_admin._apps:
    firebase_admin.initialize_app()

db = firestore.client(database_id="firestore01")

# --- 2. PAGE CONFIGURATION & AUTO-REFRESH ---
st.set_page_config(page_title="AI Tech News Aggregator", page_icon="📈", layout="wide")
count = st_autorefresh(interval=10000, limit=100, key="news_ticker")

# --- 3. FETCH LIVE CLOUD DATA ---
def fetch_live_news():
    # Pull the latest 20 articles from Firestore, ordered by published date
    docs = db.collection("articles").order_by("Published_Date", direction=firestore.Query.DESCENDING).limit(20).stream()
    
    data = []
    for doc in docs:
        data.append(doc.to_dict())
        
    return pd.DataFrame(data)

df = fetch_live_news()

# --- 4. HEADER SECTION ---
st.title("🚀 Live Data Engineering Intelligence Feed (2026)")
st.markdown("Automated AI-driven aggregator for career growth. Polling securely from GCP Firestore.")
st.divider()

# --- 5. LAYOUT: THE NEWS FEED ---
st.header("Latest Extraction & Analysis")

if df.empty:
    st.info("Waiting for data. Run your ingestion pipeline to populate the database!")
else:
    for index, row in df.iterrows():
        with st.container():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                # Make the title a clickable hyperlink
                st.subheader(f"[{row.get('Title', 'No Title')}]({row.get('URL', '#')})")
                st.caption(f"Source: {row.get('Source', 'Unknown')} | Published: {row.get('Published_Date', '')}")
                st.write(f"**AI Summary:** {row.get('Summary', 'N/A')}")
                st.write(f"**Tagged Skills:** `{row.get('Extracted_Tech', 'N/A')}`")
                
            with col2:
                sentiment = row.get('Sentiment', 'Neutral')
                if "Emerging" in sentiment:
                    st.success(sentiment)
                elif "Declining" in sentiment:
                    st.error(sentiment)
                else:
                    st.warning(sentiment)
                    
            st.divider()

# --- 6. SIDEBAR: SYSTEM STATUS ---
st.sidebar.title("System Status")
st.sidebar.success("🟢 GCP Firestore: Connected")
st.sidebar.info(f"Last UI sync: {time.strftime('%H:%M:%S')}")
st.sidebar.caption("Auto-refresh active. Polling cloud every 10s.")
