import ingest_rss
import intelligence_layer
import database

def run_pipeline():
    print("🚀 Starting Data Engineering News Pipeline...")
    
    # 1. Ingest
    raw_data = ingest_rss.fetch_news() # Assuming you have a fetch_news function in ingest_rss.py
    
    # 2. Transform/Enrich
    enriched_data = intelligence_layer.enrich_dataframe(raw_data)
    
    # 3. Load
    database.push_to_firestore(enriched_data)
    
    print("✅ Pipeline finished successfully.")

if __name__ == "__main__":
    run_pipeline()
