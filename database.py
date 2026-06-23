import firebase_admin
from firebase_admin import firestore
from google.cloud import firestore as google_firestore
import hashlib
import os

# 1. Initialize the Firebase Admin SDK 
if not firebase_admin._apps:
    firebase_admin.initialize_app()

def push_to_firestore(df, collection_name="articles"):
    """
    Takes an enriched Pandas DataFrame and pushes each row to Firestore.
    Uses the article URL as a unique ID to prevent duplicates.
    """
    if df.empty:
        print("No data to push to Firestore.")
        return

    print(f"\n☁️ Pushing {len(df)} articles to Firestore collection: '{collection_name}'...")
    
    database_id = os.environ.get("FIRESTORE_DATABASE_ID", "firestore01")

    try:
        db = firestore.client(database_id=database_id)
    except TypeError:
        db = google_firestore.Client(database=database_id)

    # Reference to your specific collection
    collection_ref = db.collection(collection_name)
    
    success_count = 0
    for index, row in df.iterrows():
        try:
            # We hash the URL to create a unique, safe Document ID.
            # This ensures if we run the script twice, it UPDATES the existing article 
            # rather than creating duplicate entries.
            doc_id = hashlib.md5(row['URL'].encode('utf-8')).hexdigest()
            
            # Convert the Pandas Series row into a standard Python dictionary
            article_data = row.to_dict()
            
            # Push to Firestore
            collection_ref.document(doc_id).set(article_data)
            success_count += 1
            
        except Exception as e:
            print(f"❌ Failed to push article '{row['Title'][:30]}...': {e}")
            
    print(f"✅ Successfully synced {success_count} articles to the cloud!")
