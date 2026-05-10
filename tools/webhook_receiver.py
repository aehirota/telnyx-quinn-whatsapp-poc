"""Flask webhook receiver — entry point for inbound WhatsApp messages to Quinn.

Run with: python tools/webhook_receiver.py
Then POST a Telnyx-shaped payload to http://localhost:5000/webhook
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify, request

PROJECT_DIR = Path(__file__).parent.parent
load_dotenv(PROJECT_DIR / ".env")
sys.path.insert(0, str(PROJECT_DIR))

from tools.language_detector import detect_language
from tools.qualification_engine import qualify
from tools.response_generator import generate_reply
from tools.salesforce_logger import log_lead

app = Flask(__name__)


@app.get("/health")
def health():
    return jsonify(status="ok")


@app.post("/webhook")
def webhook():
    body = request.get_json(silent=True)
    if not body:
        return jsonify(error="invalid or missing JSON body"), 400

    data = body.get("data") or {}
    if data.get("event_type") != "message.received":
        return jsonify(status="ignored", reason="not a message.received event"), 202

    payload = data.get("payload") or {}
    text = payload.get("text", "")
    sender = payload.get("from") or {}
    phone = sender.get("phone_number", "")
    profile_name = sender.get("profile_name")
    telnyx_message_id = payload.get("id", "")
    received_at = payload.get("received_at", "")

    if not text or not phone or not telnyx_message_id:
        return jsonify(error="missing required fields: text, from.phone_number, id"), 400

    language_detection = detect_language(text)
    qualification = qualify(text, sender_name=profile_name, language=language_detection["language"])
    reply = generate_reply(text, qualification, sender_name=profile_name)
    record = log_lead(
        telnyx_message_id=telnyx_message_id,
        phone=phone,
        name=profile_name,
        original_message=text,
        language_detection=language_detection,
        qualification=qualification,
        quinn_reply=reply,
        received_at=received_at,
    )

    return jsonify(
        language_detection=language_detection,
        qualification=qualification,
        reply=reply,
        salesforce_record_id=record["record_id"],
    )


if __name__ == "__main__":
    port = int(os.getenv("WEBHOOK_PORT", "5050"))
    print(f"Quinn WhatsApp webhook listening on http://localhost:{port}/webhook")
    app.run(host="0.0.0.0", port=port, debug=False)
