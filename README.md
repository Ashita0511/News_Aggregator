# AI-Powered Data Engineering Career Aggregator

## Overview
A serverless, automated intelligence platform that curates and analyzes Data Engineering trends in real-time. This system removes the "noise" of manual news gathering by autonomously ingesting RSS feeds, processing content via LLMs to extract actionable career insights, and serving them through a live interactive dashboard.

## Architectural Highlights
- **Serverless Ingestion:** Automated Cloud Run Jobs (batch) that run on a cron schedule.
- **AI-Native Enrichment:** Integrated Google Gemini API to extract technology stacks, sentiment, and concise TL;DRs from unstructured article text.
- **DataOps Lifecycle:** Built with infrastructure-as-code (gcloud CLI) and containerized via Docker for consistent environment parity.
- **Real-Time UI:** Built with Streamlit, providing low-latency visualization of processed data from Google Cloud Firestore.

## Tech Stack
- **Languages:** Python 3.11+
- **Cloud:** Google Cloud Run (Jobs & Services), Firestore
- **AI/LLM:** Google GenAI SDK (Gemini 2.0 Flash)
- **Data Ingestion:** `feedparser`, `requests`, `pandas`
- **Frontend:** Streamlit

## Data Flow
1. **Fetch:** Ingestion scripts pull latest RSS feeds for "Data Engineering" related content.
2. **Transform:** Raw text is passed to Gemini to extract technical metadata (e.g., Kafka, Iceberg) and determine sentiment.
3. **Load:** Enriched data is pushed to Firestore with unique document IDs based on URL hashes to prevent duplicates.
4. **Visualize:** Streamlit dashboard polls Firestore to display the latest actionable career intelligence.

## Setup & Deployment
### Prerequisites
- Google Cloud Project with Firestore (Datastore mode) enabled.
- Gemini API Key.

### Local Development
```bash
# Set credentials
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"
export GEMINI_API_KEY="your-api-key"

# Install dependencies
pip install -r requirements.txt

# Run the pipeline
python3 main.py

# Run the UI
streamlit run app.py
