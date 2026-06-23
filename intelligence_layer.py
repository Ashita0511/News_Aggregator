import os
import json
import time
import pandas as pd
from google import genai
from google.genai import types

ALLOWED_SENTIMENTS = {
    "🚀 Emerging/Learn Next",
    "⚠️ Declining/Deprecating",
    "Neutral",
}

RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "Extracted_Tech": {
            "type": "string",
            "description": "Comma-separated tools or technologies mentioned.",
        },
        "Sentiment": {
            "type": "string",
            "enum": list(ALLOWED_SENTIMENTS),
        },
        "Summary": {
            "type": "string",
            "description": "A concise 2-sentence TL;DR of the article.",
        },
    },
    "required": ["Extracted_Tech", "Sentiment", "Summary"],
}

def get_gemini_client():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set.")

    return genai.Client(api_key=api_key)

def process_with_llm(raw_text):
    """
    Passes raw article text to the LLM with strict prompt engineering
    to extract trends, sentiment, and a structured summary.
    """
    # If the article is empty, skip the API call to save resources
    if not raw_text or len(raw_text) < 20:
        return {
            "Extracted_Tech": "N/A",
            "Sentiment": "Neutral",
            "Summary": "Insufficient text to generate a summary."
        }

    # 1. Strict Prompt Engineering
    prompt = f"""
    You are an expert Data Engineering career advisor. Read the following article summary and extract key insights.
    Return ONLY a valid JSON object with the exact following schema, with no markdown formatting or extra text:
    {{
        "Extracted_Tech": "Comma separated list of tools/tech mentioned (e.g., Apache Kafka, Flink, Iceberg)",
        "Sentiment": "Must be exactly one of: '🚀 Emerging/Learn Next' OR '⚠️ Declining/Deprecating' OR 'Neutral'",
        "Summary": "A concise 2-sentence TL;DR of the article."
    }}

    Article Text:
    {raw_text}
    """

    try:
        # 2. Call the LLM
        client = get_gemini_client()
        response = client.models.generate_content(
            model=os.environ.get("GEMINI_MODEL", "gemini-2.5-flash"),
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=RESPONSE_SCHEMA,
            ),
        )
        
        # 3. Clean and parse the JSON output
        clean_json = response.text.replace('```json', '').replace('```', '').strip()
        result = json.loads(clean_json)

        if result.get("Sentiment") not in ALLOWED_SENTIMENTS:
            result["Sentiment"] = "Neutral"

        return result
        
    except Exception as e:
        print(f"⚠️ Error processing text with LLM: {type(e).__name__}: {e}")
        # Fallback schema to prevent pipeline failure
        return {
            "Extracted_Tech": "Processing Error",
            "Sentiment": "Neutral",
            "Summary": "Could not generate AI summary due to an API error."
        }

def enrich_dataframe(df):
    """
    Iterates through the raw DataFrame and applies the LLM processing to each article.
    """
    if df.empty:
        print("DataFrame is empty. Skipping LLM enrichment.")
        return df

    print("\n🧠 Starting AI enrichment process...")
    
    extracted_tech_list = []
    sentiment_list = []
    summary_list = []

    total_to_process = min(len(df), 3)
    print(f"⚠️ DEV MODE ACTIVE: Only processing top {total_to_process} articles to save quota.")

    df_subset = df.head(total_to_process)

    # 4. Iterate over the ingested articles
    for index, row in df_subset.iterrows():
        print(f"Analyzing article {index + 1}/{total_to_process}: {row['Title'][:40]}...")
        
        time.sleep(4) # Keep the pacing to avoid RPM rate limits
        
        llm_result = process_with_llm(row['Raw_Content'])
        
        extracted_tech_list.append(llm_result.get('Extracted_Tech', 'N/A'))
        sentiment_list.append(llm_result.get('Sentiment', 'Neutral'))
        summary_list.append(llm_result.get('Summary', 'N/A'))

    # Overwrite the dataframe with our processed subset
    df_subset = df_subset.copy()
    df_subset['Extracted_Tech'] = extracted_tech_list
    df_subset['Sentiment'] = sentiment_list
    df_subset['Summary'] = summary_list
    df_subset = df_subset.drop(columns=['Raw_Content'])

    return df_subset
