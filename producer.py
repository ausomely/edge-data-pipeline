import json
import random
import time
from datetime import datetime, timezone
import requests

# 1. Configuration Target
# For now, point this locally. Later we'll change this to the live Cloudflare URL
# GATEWAY_URL = "https://localhost:8787"

# Wrangler hosting the local server
# GATEWAY_URL = "http://127.0.0.1:8787"

# Brand new live public cloud URL
GATEWAY_URL = "https://clickstream-gateway.jackieau-data.workers.dev"

# 2. Mock Data Pools (Lists)
# These represent catagorical variables you'd track from real website users.
EVENT_TYPES = ["page_view", "add_to_cart", "click_signup", "checkout_success"]
DEVICE_TYPES = ["desktop", "mobile", "tablet"]
PAGES = ["/home", "/product/101", "/pricing", "/checkout", "/blog"]

def generate_mock_event():
    """
    Generates a single user interaction event.
    Demonstrates dictionary manipulation and the random module.
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

def stream_data(num_events=30):
    """
    Loops a specific number of times, generates an event,
    and streams it via an HTTP POST request.
    """
    print(f"🚀 Starting stream of {num_events} events to {GATEWAY_URL}...")
    
    for i in range(num_events):
        event = generate_mock_event()

        try:
            # Send the payload over the network as a JSON object
            response = requests.post(GATEWAY_URL, json=event, timeout=5)
            print(f"[{i+1}/{num_events}] Sent {event['event_type']} - Server Response Status: {response.status_code}")
        except requests.exceptions.RequestException as e:
            # Catch network connection errors gracefully if the endpoint is offline
            print(f"❌ Connection check: Server is offline, but event {event['event_id']} was generated successfully.")

        # Add a random pause between 0.1 and 0.8 seconds to mimic organic user clicks
        time.sleep(random.uniform(0.1, 0.8))

# The Python entry point guard
if __name__ == "__main__":
    stream_data(30)
