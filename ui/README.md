# UI — Streamlit demo front-end

A visual interface for the Quinn WhatsApp POC. Stands in for Telnyx's WhatsApp Business sender during the live demo — gives you a form to compose inbound messages and renders Quinn's qualification + reply alongside the live Salesforce mock.

## Architecture

The UI is a thin wrapper that POSTs to the existing Flask `/webhook` endpoint — exactly the way Telnyx will hit it in production. **The Flask + tools layer is unchanged.**

```
[browser]
   │
   ▼
[Streamlit · ui/app.py]   ──POST──▶   [Flask /webhook]   ──▶   [4 tools]   ──▶   JSON response
   │                                                                                  │
   └◀──────────────── renders qualification + reply ◀────────────────────────────────┘
```

## Run

Two terminals. **Each one needs to `cd` into the project root and activate the venv first** — otherwise `python` can't find `tools/webhook_receiver.py` and `streamlit` isn't on PATH.

**Terminal 1 — Flask webhook (must start first):**
```bash
cd /path/to/telnyx-quinn-whatsapp-poc
source .venv/bin/activate
WEBHOOK_PORT=5050 python tools/webhook_receiver.py
```

**Terminal 2 — Streamlit UI:**
```bash
cd /path/to/telnyx-quinn-whatsapp-poc
source .venv/bin/activate
streamlit run ui/app.py
```

The browser auto-opens to `http://localhost:8501`. If port 8501 is taken, override with `--server.port 8502`.

Your shell prompt should show `(.venv)` after `source .venv/bin/activate`. If you see `streamlit: command not found` or `python: can't open file 'tools/webhook_receiver.py'`, the venv isn't active or you're in the wrong directory.

## Demo flow

1. The sidebar shows the current Salesforce CRM (mock JSON file). Pre-seeded with one prior lead.
2. Pick a sample from the dropdown (or compose a custom message). The form pre-fills sender phone/name/message text.
3. Click **▶ Send to Quinn**. The spinner shows "Quinn is thinking..." while Flask processes (~5–7s round trip — async-tolerant for the WhatsApp channel).
4. The qualification panel renders below: detected language, ICP fit, intent, routing decision, reasoning.
5. Quinn's reply renders as a chat bubble underneath.
6. The sidebar refreshes — new record visible.

## Idempotency demo

When you load a sample from the dropdown, the UI preserves the sample's original `telnyx_message_id`. Clicking Send twice with the same sample loaded → **same `record_id`, no duplicate row in the CRM**. This is the at-least-once delivery protection from `salesforce_logger.py`.

If you switch to "Compose custom" or modify the loaded sample, the UI generates a fresh `msg_id` so each send creates a new record.

## Files

- [`app.py`](app.py) — the entire Streamlit app (~190 lines, single file)

## What this UI is NOT

- **Not a production frontend.** Streamlit is for demos and internal tools. A real WhatsApp inbound surface is Telnyx's API + their dashboards — no human-facing UI needed in production.
- **Not multi-user.** Single-session, no auth. Streamlit Community Cloud could host it for a portfolio link, but this POC runs locally.
- **Not the only way to drive the system.** The CLI (`python main.py`) still works and is the documented fallback if the UI breaks during the live demo.
