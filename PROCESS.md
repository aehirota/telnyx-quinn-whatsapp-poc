# Process — How this POC was built

This POC was vibe-coded with Claude Code (Opus 4.7) as a thinking + coding partner. The Telnyx brief invited this framing ("show us your ability to put AI tooling to work"). What follows is a log of the key decisions made along the way — what alternatives I considered, what I picked, and where I pushed back on the AI's first instinct.

The intent is to show the *process* without the noise of a full transcript dump — and to be transparent about where judgment lived (mine) vs where execution lived (collaborative).

---

## Key decisions

### Path B vs full LangChain rewrite

**Considered** wrapping the orchestrator in `RunnableSequence` (LCEL) end-to-end vs just refactoring the two LLM-calling tools to LangChain idioms.

**Picked Path B** — the Flask handler is small and testable; LCEL adds abstraction without payoff at this scope. The "LangChain in your stack" signal lands either way. `RunnableSequence` stays in the Phase 2 list when volume justifies the tracing/retry infrastructure.

### UI first, multi-turn deferred

**Considered** multi-turn conversation memory vs a Streamlit UI as the depth-add before the demo.

**Picked UI first** — multi-turn touches the proven core (`qualification_engine`) and risks breaking what works. UI sits outside the core, ships visible polish in 2-3 hours, and CLI stays as fallback. Multi-turn became the Week 1 item in "what I'd build next" — a stronger answer than a rushed implementation.

### Pessimistic stress-test in BUSINESS_CASE.md

**Considered** ROI math at one (conservative) estimate.

**Picked three scenarios** — pessimistic / conservative / optimistic — after asking whether the math holds at much-lower inputs. The pessimistic floor (~$86K/yr) makes the case defensible at any reasonable assumption. Any reviewer can push on individual assumptions; showing the math holds even at floor inputs is harder to argue with.

### Mechanical routing rules

**Caught Claude overriding** the routing rule based on additional judgment. msg-002 was scoring `medium/medium` but routing to `marketing_nurture` instead of `sdr_followup` per the documented rule.

**Tightened the system prompt** to apply routing rules MECHANICALLY in order, first match wins. After tightening, all three demo samples route per the documented rules. Lesson: the rules already encode nuance via the scores; letting the LLM add more judgment doubles the inconsistency surface.

### LangSmith promoted to Week 1

Initially had LangSmith bundled with `RunnableSequence` in "Later." Realized on re-review that observability before going live is non-negotiable.

**Moved LangSmith to Week 1**, parallel with multi-turn. ~1 hour of setup vs "firefighting in production with no traces" — easy call once flagged. Caught it during the doc-audit pass, not during the build.

### "What I'd build next" reordering

Originally led with Salesforce/Marketo sync watchdog (Niamh's named pain in our interview).

**Reordered to lead with multi-turn** — the "what's next" list should deepen the demo'd feature first before pivoting to broader problems, otherwise it reads as "I'm losing interest in what I just built." Sync watchdog stays prominent at Week 3 — the right ordering is depth → productionize → broader pain → expansion.

### Mock format that mirrors the real Telnyx webhook shape

**Considered** an arbitrary mock JSON structure (faster to build).

**Picked** modeling the mock payload after Telnyx's actual messaging event envelope (`data.event_type`, `data.payload.from.phone_number`, etc.) with `type: "WhatsApp"` added. This way the "swap mock for real WhatsApp Business" Phase 2 task is genuinely a one-day swap, not a redesign.

---

## How I used the AI

- **Thinking partner.** Pushed back when I disagreed, asked it to defend its reasoning, accepted strong arguments and rejected weak ones. The routing-rule fix and the LangSmith reordering both started as the AI agreeing with my initial framing, then re-examining and proposing the change.

- **Builder.** Code, tests, doc edits, diagram generation, Excalidraw scene JSON, the merge script for the presentation canvas. Iteration speed was the killer feature — refactoring a prompt and re-running verification in minutes, not hours.

- **Critic.** Audited my work against the Telnyx brief, flagged the ROI articulation gap that prompted `BUSINESS_CASE.md`, pressure-tested the Fermi math, surfaced stale docs after the LangChain refactor.

The strategic calls — what to scope in, what to defer, what ordering reads best — were mine. The AI's value was iteration speed and a relentlessly-engaged second perspective that didn't tire of being challenged. That combination is the "vibe-coded POC" the brief was asking about.

---

## What's NOT here (deliberately)

- A full transcript dump. Hundreds of pages, lots of noise, some of it includes context from my broader workspace that isn't relevant to this POC.
- Time tracking. Active analysis + prompting time was a few hours; AI-execution time on top of that was significantly more. The brief framed time as "we don't expect more than 2 hours," which I read as "active human time" given the vibe-coded framing — but happy to discuss the split during the call.
- Self-congratulation. The decisions above are mostly small, defensible engineering judgment calls. The interesting part isn't that I made them — it's that AI collaboration made it cheap to make MORE of them across a 35-min interview window.
