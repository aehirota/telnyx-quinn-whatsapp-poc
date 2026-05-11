"""Streamlit UI for the Quinn WhatsApp POC.

Demo front-end. Stands in for Telnyx's WhatsApp Business sender — gives a
visual form for composing inbound messages and renders Quinn's qualification
+ reply alongside the live Salesforce mock.

Architecture: this UI POSTs to the existing Flask /webhook (same endpoint
Telnyx will hit in production). Flask + tools layer is unchanged.

Run:
    streamlit run ui/app.py

Requires the Flask webhook to be running first:
    python tools/webhook_receiver.py
"""

import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
import streamlit as st

PROJECT_DIR = Path(__file__).parent.parent
SAMPLES_FILE = PROJECT_DIR / "mock_data" / "sample_messages.json"
SALESFORCE_FILE = PROJECT_DIR / "output" / "salesforce_mock.json"
WEBHOOK_URL = f"http://localhost:{os.getenv('WEBHOOK_PORT', '5050')}/webhook"


# ---------------------------------------------------------------------------
# Data loaders
# ---------------------------------------------------------------------------

def load_samples() -> list[dict]:
    return json.loads(SAMPLES_FILE.read_text())


def load_salesforce() -> list[dict]:
    if not SALESFORCE_FILE.exists():
        return []
    return json.loads(SALESFORCE_FILE.read_text())


# ---------------------------------------------------------------------------
# Webhook payload + POST
# ---------------------------------------------------------------------------

def build_payload(phone: str, name: str, message: str, msg_id: str | None = None) -> dict:
    """Construct a Telnyx-shaped message.received envelope.

    If msg_id is provided, reuses it (preserves idempotency for re-sends of
    the same sample). Otherwise generates a fresh id.
    """
    now_iso = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    if msg_id is None:
        msg_id = f"msg_ui_{int(time.time() * 1000)}"
    return {
        "data": {
            "event_type": "message.received",
            "id": f"evt_ui_{int(time.time() * 1000)}",
            "occurred_at": now_iso,
            "payload": {
                "id": msg_id,
                "from": {"phone_number": phone, "profile_name": name},
                "to": [{"phone_number": "+15558675309"}],
                "text": message,
                "type": "WhatsApp",
                "received_at": now_iso,
            },
        },
        "meta": {"attempt": 1, "delivered_to": WEBHOOK_URL},
    }


def post_to_webhook(payload: dict) -> tuple[dict | None, str | None]:
    """POST to Flask. Returns (response_data, error_message). Exactly one is None."""
    try:
        r = requests.post(WEBHOOK_URL, json=payload, timeout=20)
    except requests.exceptions.ConnectionError:
        return None, (
            f"**Cannot reach Flask at {WEBHOOK_URL}.**\n\n"
            "Start it in a separate terminal:\n\n"
            "```bash\nWEBHOOK_PORT=5050 python tools/webhook_receiver.py\n```"
        )
    except requests.exceptions.Timeout:
        return None, "Request timed out (>20s). Claude or network may be slow — try again."

    if r.status_code != 200:
        return None, f"Webhook returned HTTP {r.status_code}:\n\n```\n{r.text}\n```"
    return r.json(), None


# ---------------------------------------------------------------------------
# UI rendering
# ---------------------------------------------------------------------------

SCORE_EMOJI = {"high": "🟢", "medium": "🟡", "low": "🔴"}
ROUTING_LABEL = {
    "sdr_followup": ("🟢", "SDR follow-up"),
    "marketing_nurture": ("🔵", "Marketing nurture"),
    "deflect": ("⚪", "Deflect"),
}


def render_qualification(qual: dict, language_detection: dict, elapsed: float, record_id: str) -> None:
    st.subheader("Quinn's qualification")

    lang = language_detection.get("language", "?")
    is_latam = language_detection.get("is_latam", False)
    latam_badge = "🌎 LATAM" if is_latam else "Non-LATAM"
    st.markdown(f"**Detected language:** `{lang}` &nbsp;·&nbsp; {latam_badge}")

    col1, col2, col3 = st.columns(3)
    col1.metric("ICP fit", f"{SCORE_EMOJI.get(qual['icp_fit'], '')} {qual['icp_fit']}")
    col2.metric("Intent", f"{SCORE_EMOJI.get(qual['intent'], '')} {qual['intent']}")
    routing_emoji, routing_label = ROUTING_LABEL.get(qual["routing"], ("", qual["routing"]))
    col3.metric("Routing", f"{routing_emoji} {routing_label}")

    if qual.get("company_guess"):
        st.markdown(f"**Company:** {qual['company_guess']}")
    st.markdown(f"**Use case:** {qual.get('use_case', '?')}")
    st.caption(f"Reasoning: {qual.get('reasoning', '?')}")

    st.caption(f"Logged: `{record_id}` &nbsp;·&nbsp; round trip: {elapsed:.2f}s")


def render_reply(reply_text: str) -> None:
    st.subheader("Quinn's reply (English, sent back via WhatsApp)")
    with st.chat_message("assistant", avatar="🤖"):
        st.markdown(reply_text)


def render_sidebar(records: list[dict]) -> None:
    st.sidebar.header("📊 Salesforce CRM (mock)")
    st.sidebar.caption(f"{len(records)} record(s)")
    if not records:
        st.sidebar.info("No leads yet — send a message to populate.")
        return
    rows = [
        {
            "Name": r.get("name") or "?",
            "Score": f"{r.get('icp_fit', '?')}/{r.get('intent', '?')}",
            "Routing": r.get("routing", "?"),
            "Lang": r.get("language", "?"),
        }
        for r in records
    ]
    st.sidebar.dataframe(rows, width="stretch", hide_index=True)


# ---------------------------------------------------------------------------
# Sample loader callback
# ---------------------------------------------------------------------------

def on_sample_change() -> None:
    """When the user picks a sample from the dropdown, pre-fill the form."""
    sel = st.session_state.sample_selector
    if sel == "— Compose custom message —":
        st.session_state.current_msg_id = None
        return
    sample = next((s for s in st.session_state.samples if s["id"] == sel), None)
    if not sample:
        return
    payload = sample["payload"]["data"]["payload"]
    st.session_state.form_phone = payload["from"].get("phone_number", "")
    st.session_state.form_name = payload["from"].get("profile_name", "")
    st.session_state.form_message = payload["text"]
    # Preserve original msg_id so re-sending the same sample is idempotent
    st.session_state.current_msg_id = payload["id"]


# ---------------------------------------------------------------------------
# Main app
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Quinn WhatsApp LATAM — POC",
    page_icon="💬",
    layout="wide",
)

st.title("Quinn WhatsApp LATAM — POC demo")
st.caption(
    "Telnyx Growth Engineer, GTM AI · Inbound WhatsApp qualification via "
    "LangChain (`ChatAnthropic` + `ChatPromptTemplate`) + Pydantic-typed structured output"
)

# Session state init
if "samples" not in st.session_state:
    st.session_state.samples = load_samples()
if "form_phone" not in st.session_state:
    st.session_state.form_phone = "+5511987654321"
if "form_name" not in st.session_state:
    st.session_state.form_name = "Mariana Costa"
if "form_message" not in st.session_state:
    st.session_state.form_message = ""
if "current_msg_id" not in st.session_state:
    st.session_state.current_msg_id = None
if "last_response" not in st.session_state:
    st.session_state.last_response = None
if "last_elapsed" not in st.session_state:
    st.session_state.last_elapsed = None

# Sidebar — refreshes on every rerun (incl. after each Send)
render_sidebar(load_salesforce())

# Composer
st.subheader("📥 Inbound WhatsApp message")

sample_options = ["— Compose custom message —"] + [s["id"] for s in st.session_state.samples]
st.selectbox(
    "Load a sample (or compose custom below)",
    sample_options,
    key="sample_selector",
    on_change=on_sample_change,
    help="Pick a pre-built sample to pre-fill the form, or leave on 'Compose custom' and type your own.",
)

col1, col2 = st.columns(2)
with col1:
    st.text_input("Sender phone", key="form_phone")
with col2:
    st.text_input("Sender profile name", key="form_name")

st.text_area(
    "Message text",
    key="form_message",
    height=100,
    placeholder="Type a message in any language — Portuguese and Spanish flag as LATAM…",
)

if st.session_state.current_msg_id:
    st.caption(
        f"💡 Sample loaded — re-sending uses message id `{st.session_state.current_msg_id}` "
        "so the Salesforce logger updates the same record (idempotency demo)."
    )

send_disabled = not st.session_state.form_message.strip()
if st.button("▶ Send to Quinn", type="primary", disabled=send_disabled, width="stretch"):
    with st.spinner("Quinn is thinking..."):
        started = time.time()
        payload = build_payload(
            phone=st.session_state.form_phone or "+5511000000000",
            name=st.session_state.form_name or "unknown",
            message=st.session_state.form_message,
            msg_id=st.session_state.current_msg_id,
        )
        response, error = post_to_webhook(payload)
        elapsed = time.time() - started

    if error:
        st.error(error)
        st.session_state.last_response = None
    else:
        st.session_state.last_response = response
        st.session_state.last_elapsed = elapsed
        st.rerun()  # refresh the sidebar with the new record

# Render the most recent response (persists across reruns)
if st.session_state.last_response:
    st.divider()
    response = st.session_state.last_response
    render_qualification(
        qual=response["qualification"],
        language_detection=response["language_detection"],
        elapsed=st.session_state.last_elapsed,
        record_id=response["salesforce_record_id"],
    )
    st.divider()
    render_reply(response["reply"])
