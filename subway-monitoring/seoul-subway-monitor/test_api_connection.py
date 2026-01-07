import sys
import os
from src.api_client import SeoulSubwayClient

def test_api():
    print("Testing Seoul Data API connection...")
    try:
        client = SeoulSubwayClient()
        # Test with Line 1
        data = client.get_realtime_positions("1호선")
        if data:
            print(f"Success! Received {len(data)} train positions for Line 1.")
            print("First train data sample:", data[0])
        else:
            print("Connected to API, but received no data (empty list). This might be due to operational hours or an API issue.")
            # Note: 3 PM (14:28) in Korea is definitely operating hours.
    except Exception as e:
        print(f"Failed to connect to API: {e}")

if __name__ == "__main__":
    test_api()
