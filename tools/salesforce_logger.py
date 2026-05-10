"""Append (or update by message id) a lead record in the mock Salesforce JSON file."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_PATH = Path(os.getenv("SALESFORCE_MOCK_PATH", "output/salesforce_mock.json"))


def log_lead(
    *,
    telnyx_message_id: str,
    phone: str,
    name: str | None,
    original_message: str,
    language_detection: dict,
    qualification: dict,
    quinn_reply: str,
    received_at: str,
    path: Path = DEFAULT_PATH,
) -> dict:
    """Write or update a lead record. Returns the record (with assigned record_id).

    Idempotent on telnyx_message_id — protects against Telnyx's at-least-once
    delivery (see workflows/whatsapp-qualification.md Step 5).
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    records = _load(path)

    record = {
        "record_id": f"lead_{int(datetime.now(timezone.utc).timestamp() * 1000)}",
        "source_channel": "WhatsApp",
        "phone": phone,
        "name": name,
        "company_guess": qualification.get("company_guess"),
        "language": language_detection.get("language"),
        "is_latam": language_detection.get("is_latam"),
        "icp_fit": qualification.get("icp_fit"),
        "intent": qualification.get("intent"),
        "routing": qualification.get("routing"),
        "use_case": qualification.get("use_case"),
        "original_message": original_message,
        "quinn_reply": quinn_reply,
        "received_at": received_at,
        "telnyx_message_id": telnyx_message_id,
        "logged_at": datetime.now(timezone.utc).isoformat(),
    }

    for i, existing in enumerate(records):
        if existing.get("telnyx_message_id") == telnyx_message_id:
            record["record_id"] = existing["record_id"]  # keep stable id on update
            records[i] = record
            _save(path, records)
            return record

    records.append(record)
    _save(path, records)
    return record


def _load(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return json.loads(path.read_text())


def _save(path: Path, records: list[dict]) -> None:
    path.write_text(json.dumps(records, indent=2, ensure_ascii=False))
