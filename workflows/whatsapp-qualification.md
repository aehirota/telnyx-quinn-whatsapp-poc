# SOP — WhatsApp Inbound Qualification

The standard operating procedure that runs every time a WhatsApp message lands
on Quinn's `/webhook` endpoint. Each step delegates to a single tool in
`tools/`. If a step changes, edit this file first, then the tool.

---

## Step 1 — Receive payload

**Tool:** `tools/webhook_receiver.py` (Flask, route `POST /webhook`)

- Parse Telnyx-shaped JSON from the request body
- Reject non-`message.received` events with HTTP 202 (acknowledged but ignored)
- Extract the user's text, sender phone, sender profile name, and Telnyx message id
- Pass the extracted fields to Step 2

If parsing fails, return HTTP 400 with `{"error": "..."}`. Don't retry — Telnyx
will redeliver.

---

## Step 2 — Detect language

**Tool:** `tools/language_detector.py`

- Run `langdetect.detect()` on the message text
- Return `{"language": "<iso-code>", "is_latam": true|false}`
- LATAM = Portuguese (`pt`) or Spanish (`es`)
- On detection failure (very short messages), default to `language: "unknown"` and `is_latam: false`

This is deterministic and does NOT call Claude — language detection is cheap
and reliable enough without an LLM.

---

## Step 3 — Qualify

**Tool:** `tools/qualification_engine.py`

Calls Claude Sonnet with this contract:

**System prompt (paraphrased — see code for exact text):**
> You are Quinn, Telnyx's AI SDR. Score this inbound WhatsApp message on two
> dimensions: ICP fit (does the sender's company match Telnyx's target
> profile — mid-market+, building communications products, technical buyer)
> and intent (are they actively evaluating now, or just browsing). Return
> strict JSON.

**Required output JSON:**
```json
{
  "icp_fit": "high" | "medium" | "low",
  "intent": "high" | "medium" | "low",
  "company_guess": "<company name extracted from message, or null>",
  "use_case": "<one-line summary of what they want>",
  "routing": "sdr_followup" | "marketing_nurture" | "deflect",
  "reasoning": "<one sentence>"
}
```

**Routing rules:**
- `icp_fit=high` AND `intent=high` → `sdr_followup` (loop in human SDR)
- `icp_fit>=medium` AND `intent>=medium` → `sdr_followup`
- `icp_fit=low` → `deflect` (polite redirect)
- Otherwise → `marketing_nurture`

If Claude returns malformed JSON, fall back to `routing: "sdr_followup"` (fail
safe — better to over-route than miss a hot lead).

---

## Step 4 — Generate reply

**Tool:** `tools/response_generator.py`

Calls Claude Sonnet again with the qualification result and the original
message. Generates Quinn's reply IN ENGLISH (per project decision — Quinn's
team is English-speaking; LATAM SDRs handle the Portuguese side once the lead
is routed).

Reply should:
- Acknowledge the inbound in 1-2 sentences
- For `sdr_followup`: ask one clarifying question + signal a human will follow up within X hours
- For `marketing_nurture`: share a relevant resource link (placeholder URL OK in POC)
- For `deflect`: politely redirect to support docs

Keep it under 280 characters — WhatsApp messages should feel native to the channel.

---

## Step 5 — Log to Salesforce

**Tool:** `tools/salesforce_logger.py`

Append a record to `output/salesforce_mock.json` with this shape:

```json
{
  "record_id": "lead_<timestamp>",
  "source_channel": "WhatsApp",
  "phone": "+55...",
  "name": "<profile_name>",
  "company_guess": "...",
  "language": "pt",
  "is_latam": true,
  "icp_fit": "high",
  "intent": "high",
  "routing": "sdr_followup",
  "original_message": "...",
  "quinn_reply": "...",
  "received_at": "<ISO-8601>",
  "telnyx_message_id": "msg_..."
}
```

If the same `telnyx_message_id` already exists, update in place rather than
duplicating (idempotency — protects against Telnyx's at-least-once delivery).

---

## Step 6 — Respond to webhook

`webhook_receiver.py` returns HTTP 200 with the full chain result as JSON:

```json
{
  "language_detection": {...},
  "qualification": {...},
  "reply": "...",
  "salesforce_record_id": "lead_..."
}
```

This response is what `main.py` pretty-prints during the live demo.

---

## Failure modes and fallbacks

| Failure | Behavior |
|---------|----------|
| Malformed inbound JSON | HTTP 400, no retry |
| `langdetect` raises | Default `language=unknown`, `is_latam=false`, continue |
| Claude API timeout (>10s) | HTTP 504, log to stderr, no Salesforce write |
| Claude returns non-JSON for qualification | Fall back to `sdr_followup` routing |
| Salesforce file write fails | HTTP 500, no retry (Telnyx will redeliver) |
