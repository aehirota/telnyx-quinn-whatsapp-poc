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

Calls Claude Sonnet via LangChain with a Pydantic-enforced output contract.

**Implementation:**
- `ChatPromptTemplate.from_messages([("system", SYSTEM_PROMPT), ("human", "...{message_text}...")])` — the prompt template
- `ChatAnthropic(model=..., max_tokens=400)` — the LLM client
- `_chain = _prompt | _llm.with_structured_output(Qualification)` — the LCEL chain with Pydantic schema enforcement

**System prompt (paraphrased — see code for exact text):**
> You are Quinn, Telnyx's AI SDR. Score this inbound WhatsApp message on two
> dimensions: ICP fit (does the sender's company match Telnyx's target
> profile — mid-market+, building communications products, technical buyer)
> and intent (are they actively evaluating now, or just browsing).
> Apply routing rules MECHANICALLY in order — do not override based on
> additional judgment.

**Output contract** (enforced by the `Qualification` Pydantic BaseModel — Claude cannot return any other shape):
```python
class Qualification(BaseModel):
    icp_fit: Literal["high", "medium", "low"]
    intent: Literal["high", "medium", "low"]
    company_guess: str | None
    use_case: str
    routing: Literal["sdr_followup", "marketing_nurture", "deflect"]
    reasoning: str
```

**Routing rules** (apply MECHANICALLY in order, first match wins — the rules already account for nuance via the icp_fit/intent scores):
1. `icp_fit=low` → `deflect` (polite redirect)
2. `icp_fit` AND `intent` both at least `medium` → `sdr_followup` (loop in human SDR)
3. else → `marketing_nurture`

**Fail-safe:** if the LangChain call raises (network timeout, schema mismatch — rare with structured output, etc.), the engine returns a hardcoded `routing: "sdr_followup"` with `reasoning: "Qualification failed; routed to SDR by fail-safe rule."` Better to over-route than miss a hot lead.

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
| LangChain network/timeout error during qualification | Caught by try/except in `qualify()`, fall back to `routing: "sdr_followup"` with explanatory reasoning |
| Pydantic `ValidationError` during qualification | Same fail-safe as above (Pydantic enforces the schema; ValidationError is rare with `with_structured_output()` since LangChain uses Claude's tool-use feature, but the wrapper catches it) |
| LangChain network/timeout error during reply generation | Exception propagates to Flask handler, returns HTTP 500 (Telnyx will redeliver) |
| Salesforce file write fails | HTTP 500, no retry (Telnyx will redeliver; logger is idempotent on next attempt) |
