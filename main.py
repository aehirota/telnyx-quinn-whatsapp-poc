"""One-shot demo runner — POSTs a sample WhatsApp payload to the running webhook.

Run BEFORE this:  python tools/webhook_receiver.py
Then run:         python main.py [--message-id msg-001-hot-latam]
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

PROJECT_DIR = Path(__file__).parent
load_dotenv(PROJECT_DIR / ".env")

SAMPLES_FILE = PROJECT_DIR / "mock_data" / "sample_messages.json"
DEFAULT_MESSAGE_ID = "msg-001-hot-latam"


def main() -> int:
    parser = argparse.ArgumentParser(description="Send a mock WhatsApp inbound to Quinn's webhook.")
    parser.add_argument("--message-id", default=DEFAULT_MESSAGE_ID, help="ID of the sample message to send (see mock_data/sample_messages.json)")
    parser.add_argument("--port", default=os.getenv("WEBHOOK_PORT", "5000"), help="Port the webhook is listening on")
    args = parser.parse_args()

    samples = json.loads(SAMPLES_FILE.read_text())
    sample = next((s for s in samples if s["id"] == args.message_id), None)
    if not sample:
        ids = ", ".join(s["id"] for s in samples)
        print(f"Error: message id '{args.message_id}' not found. Available: {ids}", file=sys.stderr)
        return 1

    url = f"http://localhost:{args.port}/webhook"
    payload = sample["payload"]
    msg_text = payload["data"]["payload"]["text"]
    sender = payload["data"]["payload"]["from"].get("profile_name", "unknown")

    _print_header(sample, sender, msg_text, url)
    print("Quinn is thinking...")
    started = time.time()

    try:
        response = requests.post(url, json=payload, timeout=15)
    except requests.exceptions.ConnectionError:
        print(f"\nError: cannot connect to {url}. Is the webhook running?")
        print("Start it with: python tools/webhook_receiver.py")
        return 1

    elapsed = time.time() - started

    if response.status_code != 200:
        print(f"\nWebhook returned {response.status_code}: {response.text}")
        return 1

    _print_result(response.json(), elapsed)
    return 0


def _print_header(sample: dict, sender: str, msg_text: str, url: str) -> None:
    print("=" * 72)
    print(f"DEMO  {sample['id']}  ({sample['description']})")
    print("=" * 72)
    print(f"From: {sender}")
    print(f"Message: {msg_text}")
    print(f"POST -> {url}\n")


def _print_result(result: dict, elapsed: float) -> None:
    lang = result["language_detection"]
    qual = result["qualification"]

    print()
    print("-" * 72)
    print(f"Language detected:  {lang['language']}  (LATAM: {lang['is_latam']})")
    print("-" * 72)
    print(f"ICP fit:    {qual['icp_fit']}")
    print(f"Intent:     {qual['intent']}")
    print(f"Company:    {qual.get('company_guess')}")
    print(f"Use case:   {qual.get('use_case')}")
    print(f"Routing:    {qual['routing']}")
    print(f"Reasoning:  {qual['reasoning']}")
    print("-" * 72)
    print("Quinn's reply:")
    print(f"  {result['reply']}")
    print("-" * 72)
    print(f"Logged to Salesforce as record_id: {result['salesforce_record_id']}")
    print(f"Total round trip: {elapsed:.2f}s")
    print("=" * 72)


if __name__ == "__main__":
    sys.exit(main())
