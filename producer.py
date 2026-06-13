import json
import random
import time
from datetime import datetime, timezone
import requests

# 1. Configuration Target
GATEWAY_URL = "https://clickstream-gateway.jackieau-data.workers.dev"

# 2. Mock Data Pools (Lists)
# These represent catagorical variables you'd track from real website users.
EVENT_TYPES = ["page_view", "add_to_cart", "click_signup", "checkout_success"]
DEVICE_TYPES = ["desktop", "mobile", "tablet"]
PAGES = ["/home", "/product/101", "/pricing", "/checkout", "/blog"]

def generate_raw_event():
    """
    Generates a single user interaction event.
    Demonstrates dictionary manipulation and the random module.
    This generates a structurally perfect event baseline.
    """
    return {
        "event_id": str(random.randint(100000, 999999)),
        "user_id": f"USR_{random.randint(1000, 9999)}",
        "timestamp": datetime.now(timezone.utc).isoformat(), # Standard ISO timestamp string
        "event_type": random.choice(EVENT_TYPES),
        "page_path": random.choice(PAGES),
        "device": random.choice(DEVICE_TYPES),
        "duration_seconds": round(random.uniform(0.5, 45.0), 2) # Random decimal
    }

def inject_messiness(event):
    """
    Deliberately corrupts data a small percentage of the time.
    This creates the specific data quality issues we will solve later using SQL.
    """
    # Issue A: 5% of data has missing user IDs (Crucial for testing COALENSCE)
    if random.random() < 0.05:
        event["user_id"] = None
    
    # Issue B: 5% of data has inconsistent, messy uppercase paths (Testing string cleaning)
    if random.random() < 0.05:
        event["page_path"] = event["page_path"].upper()

    return event

def stream_data_with_batching(batch_size=20, total_batches=5):
    """
    Returns a controlled loop that groups messy events into batches
    before sending them over the network, optimizing R2 operations.
    """

    print(f"🚀 Starting stream. Sending {total_batches} total batches ({batch_size} events per batch) to {GATEWAY_URL}...\n")

    for batch_num in range(total_batches):
        batch_list = []

        # Fill up our micro-batch in local memory
        for _ in range(batch_size):
            raw_event = generate_raw_event()
            messy_event = inject_messiness(raw_event)
            batch_list.append(messy_event)

            # Issue C: 2% of the time, immediately duplicate the record into the batch
            # (This perfectly emulates netowrk retry duplicates for SQL window functions)
            if random.random() < 0.02:
                batch_list.append(messy_event.copy())

        try:
            # Send the entire list array as a single network call
            response = requests.post(GATEWAY_URL, json=batch_list, timeout=5)
            print(f"📦 [Batch {batch_num + 1}/{total_batches}] Sent {len(batch_list)} events. Status: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"❌ Network Error on Batch {batch_num + 1}. Endpoint might be offline.")

        # Brief pause between batches to keep the stream fluid
        time.sleep(1.5)

if __name__ == "__main__":
    # Test run: 5 batches of 20 events = ~ 100 events sent via only 5 API calls!
    stream_data_with_batching(batch_size=20, total_batches=5)