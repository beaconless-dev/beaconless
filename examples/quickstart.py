"""Minimal end-to-end example.

    export BEACONLESS_API_KEY=sk_live_...
    python examples/quickstart.py

Docs: https://beaconless-api.pages.dev/api-reference
"""
from beaconless import Client

client = Client()  # reads BEACONLESS_API_KEY from the environment

# Push a couple of readings.
receipt = client.ingest(
    [
        {"kind": "temp", "value": 4.1, "unit": "C"},
        {"kind": "door", "value": "open"},
    ]
)
print("ingested:", receipt)

# Read the most recent events back.
for event in client.events(limit=10):
    print(event.get("ts"), event.get("kind"), event.get("value"))
