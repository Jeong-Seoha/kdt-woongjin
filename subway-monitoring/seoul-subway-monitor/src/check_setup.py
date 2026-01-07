import sys
import os
from src.config import Config
from src.db_client import SupabaseClient
from src.api_client import SeoulSubwayClient

def check_setup():
    print("Checking setup...")
    
    # Check 1: API Key and API Connection
    print("\n[1/3] Checking API Connection...")
    try:
        client = SeoulSubwayClient()
        data = client.get_realtime_positions("1호선")
        if data is not None:
             print(f"✅ API Connection Successful. Retrieved {len(data)} records for Line 1.")
        else:
             print("⚠️ API Connection returned None/Empty list (might be late night or error).")
    except Exception as e:
        print(f"❌ API Connection Failed: {e}")
        return

    # Check 2: DB Connection
    print("\n[2/3] Checking DB Connection...")
    try:
        db = SupabaseClient()
        # Just check if we can access the client object, actual logic involves a request
        if db.client:
            print("✅ DB Client Initialized.")
        else:
            print("❌ DB Client Initialization Failed.")
            return
    except Exception as e:
        print(f"❌ DB Client Init Error: {e}")
        return

    # Check 3: Table Existence
    print("\n[3/3] Checking Table 'realtime_subway_positions'...")
    try:
        # Try to select 1 row
        res = db.client.table("realtime_subway_positions").select("*", count="exact").limit(1).execute()
        print("✅ Table exists and is accessible.")
        print(f"Current row count (approx): {res.count}")
    except Exception as e:
        print(f"❌ Table Check Failed: {e}")
        print("Please ensure you have run 'docs/schema.sql' in your Supabase SQL Editor.")

if __name__ == "__main__":
    check_setup()
