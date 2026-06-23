import streamlit as st
import pandas as pd
from streamlit_autorefresh import st_autorefresh
import firebase_admin
from firebase_admin import firestore
from google.cloud import firestore as google_firestore
import os
import time

# --- 1. PAGE CONFIGURATION & AUTO-REFRESH ---
st.set_page_config(page_title="AI Tech News Aggregator", page_icon="📈", layout="wide")
count = st_autorefresh(interval=10000, limit=100, key="news_ticker")

@st.cache_resource
def get_firestore_client():
    # Streamlit reruns this script often. Cache the Firestore client so the
    # Firebase app is initialized only once per container.
    if not firebase_admin._apps:
        firebase_admin.initialize_app()

    database_id = os.environ.get("FIRESTORE_DATABASE_ID", "firestore01")

    try:
        return firestore.client(database_id=database_id)
    except TypeError:
        return google_firestore.Client(database=database_id)

# --- 2. FETCH LIVE CLOUD DATA ---
def fetch_live_news():
    db = get_firestore_client()
    docs = (
        db.collection("articles")
        .order_by("Published_Date", direction=firestore.Query.DESCENDING)
        .limit(20)
        .stream()
    )

    data = []
    for doc in docs:
        data.append(doc.to_dict())

    return pd.DataFrame(data)

try:
    df = fetch_live_news()
    firestore_error = None
except Exception as exc:
    df = pd.DataFrame()
    firestore_error = exc

# --- 3. HEADER SECTION ---
st.title("🚀 Live Data Engineering Intelligence Feed (2026)")
st.markdown("Automated AI-driven aggregator for career growth. Polling securely from GCP Firestore.")
st.divider()

# --- 4. LAYOUT: THE NEWS FEED ---
st.header("Latest Extraction & Analysis")

if firestore_error:
    st.error(f"Could not read from Firestore: {firestore_error}")
elif df.empty:
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

# --- 5. SIDEBAR: SYSTEM STATUS ---
st.sidebar.title("System Status")
if firestore_error:
    st.sidebar.error("GCP Firestore: Connection issue")
else:
    st.sidebar.success("GCP Firestore: Connected")
st.sidebar.info(f"Last UI sync: {time.strftime('%H:%M:%S')}")
st.sidebar.caption("Auto-refresh active. Polling cloud every 10s.")
