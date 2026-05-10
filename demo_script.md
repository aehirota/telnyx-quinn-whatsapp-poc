# Demo Script — 35 minutes

Beat-by-beat plan. Practice the talking points, not just the code. Have the
webhook server already running before the call starts.

---

## 0:00–5:00 — Why this feature

**Key beats:**
- Telnyx is launching WhatsApp Business — your own product, imminent GA
- LATAM team just started ramping — first Portuguese-speaking SDRs hired last month
- Quinn currently has zero WhatsApp presence
- The gap: inbound LATAM leads on WhatsApp today either bounce, get a delayed email reply, or land on an SDR's personal phone
- The dogfooding angle: extending Quinn with Telnyx's own soon-to-launch product

**One line to land:**
> "No other candidate will walk in with a Telnyx-on-Telnyx demo. That's the
> point — every channel Telnyx ships should be a channel Quinn already speaks."

---

## 5:00–20:00 — Live demo

**Setup checklist (do this BEFORE the call):**
- [ ] Webhook running: `python tools/webhook_receiver.py` in a visible terminal
- [ ] `.env` loaded with `ANTHROPIC_API_KEY`
- [ ] `output/salesforce_mock.json` exists with one pre-seeded lead (so it's not an empty-state demo)
- [ ] Second terminal open, ready to run `python main.py`

**Demo sequence:**

1. **Show the pre-seeded "CRM"** — `cat output/salesforce_mock.json` → one prior lead, source=WhatsApp
2. **Hot lead** — `python main.py` → fintech named Conta Simples, hot ICP + intent, routed to SDR, reply asks one clarifying question
3. **Warm lead** — `python main.py --message-id msg-002-warm-latam` → exploratory, marketing nurture, reply shares a doc link
4. **Cold deflect** — `python main.py --message-id msg-003-cold-noise` → consumer asking about a lost phone, deflected politely
5. **Show Salesforce** — `cat output/salesforce_mock.json` → all three new leads logged with full qualification context

**What to call out while it runs:**
- The latency (~5–7 seconds end-to-end — fast for an async channel where users tolerate seconds-to-minutes for human replies; the "Quinn is thinking..." indicator covers it)
- The qualification reasoning Claude returns — not just a score, an explanation, enforced by the Pydantic schema
- The reply tone — native to WhatsApp, not corporate email
- The idempotency — running the same message twice updates the same record (`telnyx_message_id` is the dedupe key)

---

## 20:00–25:00 — Code walkthrough

Open in this order, ~1 minute each:

1. **`workflows/whatsapp-qualification.md`** — the SOP. "I always write the workflow before the code. The SOP is stack-agnostic; the tools implement it."
2. **`tools/webhook_receiver.py`** — Flask, ~70 lines. Wires the four tools together. Sequential pipeline because each tool has a real data dependency on the previous one.
3. **`tools/qualification_engine.py`** — `ChatAnthropic` + `ChatPromptTemplate` + Pydantic `Qualification` schema with `Literal` enums + `.with_structured_output()`. Show the routing rules in the system prompt and the schema-enforced contract — no manual JSON parsing.
4. **`tools/response_generator.py`** — `ChatAnthropic` + `ChatPromptTemplate`, English-only directive baked into the system prompt.
5. **`tools/salesforce_logger.py`** — show the idempotency on `telnyx_message_id`.

**One line to land:**
> "Built in LangChain idioms because that's your stack — `ChatAnthropic`,
> `ChatPromptTemplate`, Pydantic-typed structured output. Flask is the
> orchestrator now; natural Phase 2 is `RunnableSequence` for retry +
> LangSmith tracing. Same architecture, just heavier infrastructure once
> volume justifies it."

---

## 25:00–30:00 — Trade-offs and what breaks at scale

**What's intentionally not in the POC:**
- **No retry logic** — Telnyx redelivers (at-least-once), the logger is idempotent on `telnyx_message_id`. The channel itself gives us the durability that a workflow engine would normally provide.
- **No `RunnableSequence` wrapper** — Flask handler is small and testable. LCEL adds abstraction without payoff at this scope. Phase 2 once we want LangSmith tracing.
- **No queue** — synchronous request/response works for the load profile. If we ever needed sub-second responses (e.g., voice channel), we'd put qualification on Celery/RQ.
- **No model fallback** — if Claude is down, Quinn is down. In prod we'd cache common qualification patterns or fall back to a simple keyword classifier for the deflect path.

**What breaks at scale:**
- **JSON file as Salesforce** — obviously a real CRM in prod (one-day swap with `simple-salesforce`).
- **One Claude call per message** — at 100k inbound/month that's a real cost line. Mitigations: cache repeat senders, use Haiku for the deflect path (no SDR follow-up needed).
- **Single-message scoring** — multi-turn conversations need conversation memory (LangChain `ChatMessageHistory`), which is a Phase 2 feature.
- **Sequential pipeline** — works while every step has a data dependency. When we add parallel enrichment (e.g., Salesforce lookup of the sender's company), we'd refactor to `RunnableParallel`.

---

## 30:00–35:00 — What I'd build next

Frame this as: "You hired me, what does week one and week two look like?"

1. **Week 1 — Salesforce/Marketo sync watchdog.** Niamh named the lag pain explicitly in our interview. This addresses it directly: monitor sync delays, alert before they become attribution problems, optionally trigger backfills. Same architecture — LangChain tools, Claude as the reasoner, SOP-first design. Ship in week one.

2. **Week 2 — Live Telnyx WhatsApp Business.** Once GA credentials exist, swap the mock webhook. Less than a day of work because the contract is already defined in the SOP.

3. **Week 3 — Outbound WhatsApp sequences.** Today Quinn outbounds via 10 mailboxes. Adding WhatsApp as an outbound channel for LATAM doubles the surface area without doubling the SDR cost.

4. **Week 4+ — Conversation memory.** Multi-turn qualification flow. The single-message demo is the floor, not the ceiling.

**Closing line:**
> "The reason this took two days, not two weeks, is that the architecture
> separates reasoning from execution and lives in your stack. Claude reasons via
> LangChain. Tools execute. The SOP describes the contract. New channels, new
> pain points, new integrations — they slot into the same pattern. That's the
> stack I want to build at Telnyx."
