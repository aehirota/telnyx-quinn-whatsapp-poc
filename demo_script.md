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

**Open `BUSINESS_CASE.md` on screen for the last ~90 seconds of this section** — walk through the three scenarios in the TL;DR table:
- *"Even at the pessimistic floor — 15 messages/week, low ACV — it's ~$86K/year. Pays back the build inside one quarter."*
- *"Conservative at today's volume: ~$420K/year incremental ARR plus dogfooding case-study value."*
- *"Post-WhatsApp-Business-GA: ~$5-19M/year depending on volume scaling."*
- *"The math holds even if every input is wrong by 2-3x. The asymmetric downside is the real argument: every LATAM message after GA without Quinn coverage is a leak."*

**One line to land:**
> "No other candidate will walk in with a Telnyx-on-Telnyx demo. That's the
> point — every channel Telnyx ships should be a channel Quinn already speaks."

---

## 5:00–20:00 — Live demo

**Setup checklist (do this BEFORE the call):**
- [ ] Webhook running on port 5050: `WEBHOOK_PORT=5050 python tools/webhook_receiver.py` in a visible terminal (port 5050 is the default; AirPlay Receiver squats on 5000 on macOS)
- [ ] Streamlit UI running: `streamlit run ui/app.py` in a second terminal — browser auto-opens at `http://localhost:8501`
- [ ] `.env` loaded with `ANTHROPIC_API_KEY` and `WEBHOOK_PORT=5050`
- [ ] `output/salesforce_mock.json` reset to just the Lucas Pereira seed (`git checkout output/salesforce_mock.json` if needed)
- [ ] Browser tab on the Streamlit URL, sized to fit the share-screen
- [ ] One smoke test before the call: load msg-001 in the UI → click Send → verify it works, then reset the mock again
- [ ] Third terminal open as a CLI fallback, ready to run `python main.py` if the UI breaks

**If something breaks live:**
- Webhook crashed → Ctrl+C the runaway, restart `WEBHOOK_PORT=5050 python tools/webhook_receiver.py`, retry the UI
- Streamlit crashed / browser broken → drop to CLI demo: `python main.py --message-id msg-001-hot-latam`
- Network/Claude error → fall back to the pre-seeded record: "Here's a previous run from yesterday — the architecture is the same"
- Terminal output garbled → `clear && python main.py` to give a clean frame
- All else fails → switch to the architecture diagram + code walkthrough early; you've already shown the demo works in your README and the diagrams folder

**Demo sequence (with UI):**

1. **Show the pre-seeded CRM** — point at the Streamlit sidebar: one prior lead (Lucas Pereira/Olist) with source=WhatsApp. "This is what's already in Salesforce before any new inbound."
2. **Hot lead** — pick `msg-001-hot-latam` from the dropdown → form pre-fills (Mariana Costa, Conta Simples message) → click ▶ Send to Quinn. Watch the panel render: `high/high → sdr_followup`, Quinn's reply asking call volume + promising 4-hour SDR follow-up. Sidebar updates with the new record.
3. **Warm lead** — pick `msg-002-warm-latam` → Send. Land the warm-lead callout: `medium/medium → sdr_followup` is deliberate ("I tuned the rule to err on routing to humans"). Reply asks expected monthly volume.
4. **Cold deflect** — pick `msg-003-cold-noise` → Send. `low/low → deflect`, Quinn politely redirects to mobile carrier. "Quinn knows when not to engage."
5. **Custom message on the spot** — switch dropdown to "Compose custom" → type something fresh: `"Olá, sou da Nubank, estamos avaliando voice API para nosso suporte. Podemos conversar?"` → Send. Show Quinn handling unseen input correctly. This kills the "you cherry-picked the samples" objection.
6. **Idempotency demo** — re-pick `msg-001-hot-latam` → Send. Sidebar still shows 4 records (not 5) because the logger is idempotent on `telnyx_message_id`. Point at the caption above the Send button: "Sample loaded — re-sending uses the same message id, updates the same record."

**Callout to land during the warm lead beat:**
> "You'll notice this is `medium/medium` and still routed to SDR — that's deliberate. I tuned the rule to err on routing to humans, because losing a qualified lead to a nurture sequence is more expensive than the SDR time to triage one. The `marketing_nurture` path triggers when intent is genuinely low (e.g., 'what do you do?' with no business context). None of these three samples hit that case."

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

1. **Week 1 — Multi-turn conversations.** Single-message qualification is the floor — a real LATAM lead takes 3–5 messages to qualify properly. Add LangChain `ChatMessageHistory` (or LangGraph for stateful graph orchestration) so Quinn carries context across messages from the same sender. `qualification_engine` becomes a node in a stateful graph instead of a stateless function — same contract, different orchestration layer. Most obvious depth signal for the feature I just demoed.

2. **Week 2 (or whenever WhatsApp Business ships) — Live Telnyx WhatsApp Business API.** Swap the mock webhook for real credentials. Less than a day of work because the Telnyx-shaped payload contract is already defined in `mock_data/sample_messages.json`. Timing-gated on Telnyx's own GA — when GA ships, this becomes Day 1.

3. **Week 3 — Salesforce/Marketo sync watchdog.** Niamh named the lag pain explicitly in our interview. Same architecture pattern as this POC — LangChain tools, Claude as the reasoner, SOP-first design. Monitor sync delays, alert before they become attribution problems, optionally trigger backfills. Broader Quinn-wide value, not just this channel.

4. **Week 4+ — Outbound WhatsApp sequences.** Today Quinn outbounds via 10 mailboxes. Adding WhatsApp as an outbound channel for LATAM doubles the surface area without doubling the SDR cost. This is where we'd actually need a workflow engine (Temporal, Prefect, or LangGraph) — durable timers + multi-day state. The pipeline pattern stops fitting and we graduate to a real orchestrator.

**Closing line:**
> "The reason this took two days, not two weeks, is that the architecture
> separates reasoning from execution and lives in your stack. Claude reasons via
> LangChain. Tools execute. The SOP describes the contract. New channels, new
> pain points, new integrations — they slot into the same pattern. That's the
> stack I want to build at Telnyx."
