import json
import random
import time
import io
from datetime import datetime, timezone
import pandas as pd
import requests

# 1. Configuration Target
GATEWAY_URL = "https://clickstream-gateway.jackieau-data.workers.dev"

# 2. Mock Data Pools
EVENT_TYPES = ["page_view", "add_to_cart", "click_signup", "checkout_success"]
DEVICE_TYPES = ["desktop", "mobile", "tablet"]
PAGES = ["/home", "/product/101", "/pricing", "/checkout", "/blog"]

def generate_raw_event():
    """Generates a single structural baseline clickstream event."""
    return {
        "event_id": str(random.randint(100000, 999999)),
        "user_id": f"USR_{random.randint(1000, 9999)}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_type": random.choice(EVENT_TYPES),
        "page_path": random.choice(PAGES),
        "device": random.choice(DEVICE_TYPES),
        "duration_seconds": round(random.uniform(0.5, 45.0), 2)
    }

def inject_messiness(event):
    """Deliberately corrupts data a small percentage of the time for testing."""
    if random.random() < 0.05:
        event["user_id"] = None
    if random.random() < 0.05:
        event["page_path"] = event["page_path"].upper()
    return event

def stream_data_with_batching(batch_size=20, total_batches=5):
    """
    Groups messy events into micro-batches, compresses them into columnar
    Apache Parquet files in memory, and dispatches them to the R2 gateway.
    """
    print(f"🚀 Starting stream. Optimizing payloads to Apache Parquet...")
    print(f"📡 Sending {total_batches} batches to {GATEWAY_URL}...\n")

    for batch_num in range(total_batches):
        batch_list = []

        # Fill up our micro-batch in local memory
        for _ in range(batch_size):
            raw_event = generate_raw_event()
            messy_event = inject_messiness(raw_event)
            batch_list.append(messy_event)

            # Emulate network retry duplication
            if random.random() < 0.02:
                batch_list.append(messy_event.copy())

        # --- PARQUET OPTIMIZATION LAYER ---
        # 1. Convert the list of dictionaries into a Pandas DataFrame
        df = pd.DataFrame(batch_list)
        
        # 2. Convert text data types to explicit string objects for Arrow schema stability
        string_cols = ['event_id', 'user_id', 'timestamp', 'event_type', 'page_path', 'device']
        df[string_cols] = df[string_cols].astype(str)
        
        # 3. Serialize the DataFrame into a Parquet file entirely in memory (BytesIO)
        parquet_buffer = io.BytesIO()
        df.to_parquet(parquet_buffer, engine='pyarrow', compression='snappy', index=False)
        parquet_buffer.seek(0) # Reset buffer pointer to the beginning of the stream

        try:
            # Send the binary data stream over HTTP POST
            # We change the header to alert our gateway that binary bytes are arriving instead of text JSON
            headers = {'Content-Type': 'application/octet-stream'}
            response = requests.post(GATEWAY_URL, data=parquet_buffer, headers=headers, timeout=5)
            
            print(f"📦 [Batch {batch_num + 1}/{total_batches}] Compressed {len(batch_list)} rows to Parquet. Status: {response.status_code}")

            # DEBUG: temporarily read the error body
            if response.status_code == 500:
                print(f"   ⚠️ Server Error Details: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"❌ Network Error on Batch {batch_num + 1}. Endpoint might be offline.")

        time.sleep(1.5)

if __name__ == "__main__":
    stream_data_with_batching(batch_size=20, total_batches=5)