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

- **Language:** Python 3.11+
- **LLM orchestration:** LangChain (`ChatAnthropic` + `ChatPromptTemplate` + Pydantic-typed `.with_structured_output()`)
- **LLM model:** Claude Sonnet (`claude-sonnet-4-20250514` by default; overridable via `CLAUDE_MODEL` env var)
- **Web framework:** Flask (the `/webhook` orchestrator)
- **Demo UI:** Streamlit (`ui/app.py` — default for live demo, posts to Flask)
- **CLI fallback:** `main.py` (kept as the if-UI-breaks fallback)
- **Schema enforcement:** Pydantic v2 (the `Qualification` model is the contract Claude must satisfy)
- **No:** Zapier, n8n, no-code tools, prompt playgrounds

---

## File Structure

```
telnyx-quinn-whatsapp-poc/
├── CLAUDE.md                          # This file — project charter, evaluation criteria
├── README.md                          # Setup, run, what was built and why (repo entry point)
├── BUSINESS_CASE.md                   # ROI math: 3 scenarios, assumptions, what to validate Day-1
├── demo_script.md                     # 35-minute presentation script with talk track
├── requirements.txt                   # Python deps (Flask, LangChain, Pydantic, Streamlit, etc.)
├── .env                               # API keys — never commit (gitignored)
├── .env.example                       # Template for .env
├── .gitignore                         # Excludes .env, .venv, __pycache__
├── main.py                            # CLI fallback — POSTs a sample payload to Flask
├── workflows/
│   └── whatsapp-qualification.md      # SOP for the full qualification flow (stack-agnostic)
├── tools/
│   ├── webhook_receiver.py            # Flask app — /webhook endpoint, orchestrates the pipeline
│   ├── language_detector.py           # langdetect, deterministic, no LLM
│   ├── qualification_engine.py        # LangChain + Pydantic-typed structured output
│   ├── response_generator.py          # LangChain ChatPromptTemplate + ChatAnthropic
│   └── salesforce_logger.py           # Mock Salesforce lead logger, idempotent on telnyx_message_id
├── ui/
│   ├── app.py                         # Streamlit demo UI — default for live demo
│   └── README.md                      # How to run the UI
├── mock_data/
│   ├── sample_messages.json           # 3 Telnyx-shaped sample inbounds for demo
│   └── README.md                      # Schema notes
├── output/
│   └── salesforce_mock.json           # The "CRM" — pre-seeded with one prior lead
└── diagrams/
    ├── README.md                      # Index of diagrams + when to use which format
    ├── architecture-overview.mmd      # Mermaid source (embedded in main README)
    ├── architecture-overview.excalidraw    # Standalone Excalidraw version
    ├── qualification-engine-internals.excalidraw
    ├── response-generator-internals.excalidraw
    └── presentation-canvas.excalidraw # All three diagrams stacked for live demo
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

- **Two services must be running before demo** — Flask (`tools/webhook_receiver.py`) AND Streamlit (`streamlit run ui/app.py`). Start both before the call, not during. Have a third terminal ready for the CLI fallback (`python main.py`).
- **Port 5000 is taken by macOS AirPlay Receiver** — use `WEBHOOK_PORT=5050` (already the default in `webhook_receiver.py`). Disable AirPlay Receiver in System Settings if 5050 is also taken.
- **Each terminal needs `cd` into project + `source .venv/bin/activate`** — common trip-up; you'll see `streamlit: command not found` or `python: can't open file 'tools/webhook_receiver.py'` if missed.
- **Claude API key must be in `.env` and loaded** — `ANTHROPIC_API_KEY=...`. Test the night before.
- **Mock payload must feel realistic** — use a real Brazilian company name and use case for the custom-message demo (Nubank, Stone, Conta Simples, etc.).
- **Response latency** — WhatsApp is async; 5-7s round trip from two sequential Sonnet calls is fine for the channel (users tolerate seconds-to-minutes for human replies). The "Quinn is thinking..." spinner in the Streamlit UI covers it on stage. Cost optimization (Haiku for replies, etc.) belongs in "what I'd build next," not the POC.
- **Don't demo from an empty state** — reset `output/salesforce_mock.json` to just the Lucas Pereira seed before the call (`git checkout output/salesforce_mock.json`).

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

1. **Salesforce/Marketo sync watchdog** — directly addresses the lag pain Niamh named. Same architecture (LangChain tools, Claude as the reasoner, SOP-first design).
2. **Live Telnyx WhatsApp Business API** — swap the mock webhook for real credentials once launched. The Telnyx-shaped payload contract is already defined in `mock_data/sample_messages.json`, so this is a one-day swap.
3. **Outbound WhatsApp sequences** (Day 1, Day 3, Day 7) — Quinn initiates LATAM outbound via WhatsApp, not just email. Needs a workflow engine (Temporal, Prefect, or LangGraph) for durable timers + multi-day state — the linear pipeline pattern stops fitting at this point.
4. **Conversation memory** — multi-turn qualification via LangChain `ChatMessageHistory` (or LangGraph for stateful graph orchestration). The `qualification_engine` becomes a node in a stateful graph instead of a stateless function.
5. **`@tool` schemas + `AgentExecutor`** — promote each tool from a plain function to an `@tool`-decorated callable when Quinn becomes a tool-calling agent.
6. **`RunnableSequence` + LangSmith** — wrap the orchestrator in LCEL once volume justifies the tracing/retry infrastructure.

---

## Important Reminders

- Share Claude Code session transcripts with the repo — they asked for it optionally and it
  demonstrates the vibe-coding workflow their team uses internally
- Rehearse the talking points, not just the code — the 35 minutes is a presentation, not a
  code review
- The "what I'd do next" section is evaluated equally — don't treat it as filler
