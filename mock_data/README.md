# Mock Data — Inbound WhatsApp Payloads

## Why these payloads exist

Telnyx WhatsApp Business has not launched at the time of this POC, so we cannot
hit a real webhook. These payloads simulate what a Telnyx inbound WhatsApp event
will plausibly look like — modeled after Telnyx's existing messaging webhook
shape (SMS/MMS), with `type: "WhatsApp"` added.

## Schema

Each entry in `sample_messages.json` is wrapped in a small envelope so the demo
runner can pick a specific message by ID and pretty-print its description. The
actual webhook payload is inside `.payload`.

```
{
  "id": "msg-001-hot-latam",          // demo-only handle
  "description": "...",                 // demo-only label
  "payload": { ... }                    // the actual Telnyx-shaped webhook body
}
```

The `payload` itself follows Telnyx's standard messaging event envelope:

```
{
  "data": {
    "event_type": "message.received",
    "id": "evt_...",
    "occurred_at": "ISO-8601",
    "payload": {
      "id": "msg_...",
      "from": {"phone_number": "+55...", "profile_name": "..."},
      "to": [{"phone_number": "+1..."}],
      "text": "...",
      "type": "WhatsApp",
      "received_at": "ISO-8601"
    }
  },
  "meta": {...}
}
```

## The three samples

| ID | ICP fit | Intent | Purpose in demo |
|----|---------|--------|-----------------|
| msg-001-hot-latam | High | High | Default demo message — fintech evaluating Twilio alternative |
| msg-002-warm-latam | Medium | Exploratory | Shows nuanced scoring, not just binary |
| msg-003-cold-noise | Low | N/A | Shows Quinn correctly deflecting non-prospects |

All three are in Portuguese to exercise the language detector and LATAM routing.
