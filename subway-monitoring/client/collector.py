import os
import requests
import json
import time
from datetime import datetime
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
API_KEY = os.getenv("SEOUL_API_KEY") # You need to set this in .env
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not API_KEY or not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: Missing environment variables. Please check .env file.")
    # In a real scenario, we might want to exit, but for now just warning
    # exit(1)

# API Endpoint Template
# http://swopenapi.seoul.go.kr/api/subway/{KEY}/{TYPE}/{SERVICE}/{START_INDEX}/{END_INDEX}/{subwayNm}
BASE_URL = "http://swopenapi.seoul.go.kr/api/subway"

def fetch_realtime_position(line_name: str, start_index: int = 0, end_index: int = 100):
    """
    Fetches real-time train positions for a given subway line.
    """
    if not API_KEY:
        print("Skipping API call: No API Key provided.")
        return None

    # URL Encoding for line name might be needed but requests usually handles it.
    # The API path format:
    url = f"{BASE_URL}/{API_KEY}/json/realtimePosition/{start_index}/{end_index}/{line_name}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        if 'realtimePositionList' in data:
            return data['realtimePositionList']
        elif 'RESULT' in data:
             print(f"API Error: {data['RESULT']}")
             return None
        else:
            return None

    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

def transform_data(api_data):
    """
    Transforms API data to match Supabase schema.
    """
    transformed = []
    for item in api_data:
        try:
            # Parse dates safely
            recptn_dt = item.get('recptnDt') 
            # Note: Postgres assumes UTC if not specified, or local if configured. 
            # Ideally parse to datetime object if needed, but Supabase handles ISO strings well.

            record = {
                "subway_id": item.get('subwayId'),
                "subway_name": item.get('subwayNm'),
                "station_id": item.get('statnId'),
                "station_name": item.get('statnNm'),
                "train_number": item.get('trainNo'),
                "last_reception_date": item.get('lastRecptnDt'),
                "reception_time": recptn_dt,
                "message_direction": item.get('updnLine'),
                "destination_station_id": item.get('statnTid'),
                "destination_station_name": item.get('statnTnm'),
                "train_status": item.get('trainSttus'),
                "is_express": item.get('directAt') == '1', # Convert "1"/"0" to Boolean
                "is_last_train": item.get('lstcarAt') == '1' # Convert "1"/"0" to Boolean
            }
            transformed.append(record)
        except Exception as e:
            print(f"Error transforming record: {e}, Data: {item}")
    
    return transformed

def save_to_supabase(data):
    """
    Inserts data into 'realtime_train_positions' table.
    """
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("Skipping Supabase insert: No credentials.")
        return

    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        response = supabase.table('realtime_train_positions').insert(data).execute()
        # In newer supabase-py, insert returns a response object.
        print(f"Inserted {len(data)} records.")
    except Exception as e:
        print(f"Supabase Insert Error: {e}")

def main():
    target_lines = [
        "1호선", "2호선", "3호선", "4호선", "5호선", "6호선", "7호선", "8호선", "9호선",
        "경의중앙선", "공항철도", "경춘선", "수인분당선", "신분당선", "우이신설선", "GTX-A"
    ]
    
    for line in target_lines:
        print(f"Fetching data for {line}...")
        raw_data = fetch_realtime_position(line)
        
        if raw_data:
            print(f"Received {len(raw_data)} records.")
            clean_data = transform_data(raw_data)
            save_to_supabase(clean_data)
        else:
            print("No data received.")

if __name__ == "__main__":
    main()
