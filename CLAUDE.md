# Quinn WhatsApp LATAM — Take-Home POC

## Context

Anderson is building a take-home POC for Telnyx's Growth Engineer, GTM AI role.
The challenge: build a new feature for Quinn, Telnyx's AI SDR agent.

**Chosen feature:** WhatsApp inbound qualification for the LATAM market.

**Why this feature:**
- Telnyx is launching WhatsApp Business imminently (their own product)
- LATAM sales team just started ramping — first Portuguese speakers hired last month
- Quinn currently has zero WhatsApp presence
- Demo is visual and visceral: send a WhatsApp message, watch Quinn qualify and respond

**The meta-narrative:** Telnyx sells WhatsApp Business API. This POC dogfoods their own
product to extend their own AI SDR. No other candidate will walk in with that angle.

---

## Quinn's Architecture (from interviews)

- Built in Python, hosted on Kubernetes
- Inbound: event-driven (webhook triggered)
- Outbound: scheduled jobs
- Orchestration: LangChain
- CRM: Salesforce (with known Marketo sync lag pain point)
- OpenClaw agent in Slack for BDR ad-hoc tasks
- 10 mailboxes for outbound email

---

## This POC — Scope

Build a WhatsApp inbound qualification handler that extends Quinn with:

1. **Webhook receiver** — simulates a Telnyx WhatsApp Business inbound payload
2. **Language detection** — detects Portuguese and flags as LATAM lead
3. **Qualification engine** — LLM scores ICP fit and intent, makes routing decision
4. **Response generator** — generates Quinn's reply in English
5. **Salesforce logger** — creates/updates lead object with WhatsApp as source channel

**Not in scope for POC:**
- Live Telnyx WhatsApp credentials (product not launched yet — use mock webhook)
- Full Salesforce API integration (use mock JSON logger)
- Production error handling or retry logic

---

## Stack

- **Language:** Python
- **LLM backend:** Claude API (claude-sonnet-4-20250514)
- **Web framework:** Flask (webhook receiver)
- **Demo runner:** single `main.py` entry point
- **No:** Zapier, n8n, no-code tools, prompt playgrounds

---

## File Structure

```
telnyx-quinn-whatsapp-poc/
├── CLAUDE.md                          # This file
├── .env                               # API keys — never commit
├── main.py                            # Demo entry point — runs everything
├── workflows/
│   └── whatsapp-qualification.md      # SOP for the full qualification flow
├── tools/
│   ├── webhook_receiver.py            # Flask app — receives mock WhatsApp payload
│   ├── language_detector.py           # Detects PT-BR, flags as LATAM lead
│   ├── qualification_engine.py        # LLM qualification + routing logic
│   ├── response_generator.py          # Generates Quinn's reply in English
│   └── salesforce_logger.py          # Mock Salesforce lead logger
├── mock_data/
│   └── sample_messages.json           # Sample inbound WhatsApp payloads for demo
├── README.md                          # What was built and why (for repo submission)
└── demo_script.md                     # Talking points for the 35-minute presentation
```

---

## WAT Framework Rules

This project follows the WAT framework (Workflows → Agent → Tools).

1. **Read the workflow before acting** — always check `workflows/` first
2. **Check tools before building** — reuse existing scripts, don't rebuild
3. **Execute via tools** — API calls and data transforms go in `tools/`, not inline
4. **Handle failures as learning events** — fix, retest, update workflow
5. **Never overwrite workflow files without permission**

---

## Demo Flow (35 minutes)

| Time | What happens |
|------|-------------|
| 0-5 min | Why this feature — WhatsApp launch, LATAM ramp, Quinn gap |
| 5-20 min | Live demo — send mock PT-BR message, watch Quinn qualify and respond |
| 20-25 min | Walk through the code — webhook → LLM → logger |
| 25-30 min | Trade-offs and what breaks at scale |
| 30-35 min | What I'd build next — Salesforce/Marketo watchdog as week-two feature |

---

## Demo Risk Flags

- **Flask server must be running before demo** — start it before the call, not during
- **Claude API key must be in .env and loaded** — test this the night before
- **Mock payload must feel realistic** — use a real Brazilian company name and use case
- **Response latency** — WhatsApp is async; 4-7s round trip from two sequential Sonnet calls is fine for the channel (users tolerate seconds-to-minutes for human replies). The "Quinn is thinking..." indicator in `main.py` covers it on stage. Cost optimization (Haiku for replies) belongs in "what I'd build next," not the POC.
- **Don't demo from an empty state** — pre-load one completed qualification in the logger so
  there's existing data to show before the live run

---

## Evaluation Criteria Mapping

| Criterion | How this POC addresses it |
|-----------|--------------------------|
| Creativity | Uses Telnyx's own product to extend Quinn — dogfooding angle |
| Demo quality | Visual, live, end-to-end in one command |
| ROI articulation | LATAM pipeline leakage, 24/7 coverage, BDR time freed |
| Quinn alignment | Fits inbound event-driven architecture exactly |

---

## What I'd Do Next (with more time)

1. **Salesforce/Marketo sync watchdog** — directly addresses the lag pain Niamh named
2. **Live Telnyx WhatsApp Business API** — swap mock webhook for real credentials once launched
3. **Outbound WhatsApp sequences** — Quinn initiates LATAM outbound via WhatsApp, not just email
4. **Conversation memory** — multi-turn qualification flow, not single-message scoring

---

## Important Reminders

- Share Claude Code session transcripts with the repo — they asked for it optionally and it
  demonstrates the vibe-coding workflow their team uses internally
- Rehearse the talking points, not just the code — the 35 minutes is a presentation, not a
  code review
- The "what I'd do next" section is evaluated equally — don't treat it as filler
