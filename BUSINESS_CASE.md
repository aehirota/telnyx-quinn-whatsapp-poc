# Business Case — WhatsApp inbound qualification for Quinn

> All numbers below are Fermi estimates with stated assumptions. Validating them against Telnyx's actual LATAM inbound volume, conversion data, and ACV is a Day-1 task. The shape of the math holds even if individual inputs shift by 2-3x.

---

## The problem in one paragraph

Telnyx is shipping WhatsApp Business and just hired its first Portuguese-speaking SDRs. Today, a Brazilian prospect messaging Telnyx via WhatsApp gets one of three bad outcomes: (1) no response, (2) a delayed email reply hours or days later, (3) lands on an SDR's personal phone outside business hours. Industry data on inbound-lead response time is unambiguous — instant response converts dramatically better than delayed (Drift's *State of Conversational Marketing* and HubSpot's annual sales benchmark reports both consistently show conversational-channel responses within minutes outperforming hour+ responses by an order of magnitude on qualification rate). Every LATAM WhatsApp inbound that doesn't get instant qualification is a lead either lost or significantly devalued.

This POC closes the loop: inbound message → Quinn qualifies in <7 seconds → routes to the right LATAM SDR with full context → the SDR converses with a pre-warmed lead instead of a cold one.

---

## The math (Fermi estimate)

### Volume assumptions

| Input | Conservative | Optimistic | Source / how we'd validate |
|---|---|---|---|
| LATAM WhatsApp inbound /week (today) | 25 | 75 | Pull from Telnyx's existing inbound logs by region; LATAM is small today but rising with the SDR ramp |
| Post WhatsApp Business GA (12 months out) | 5x current | 10x current | Comparable B2B SaaS WhatsApp launches saw 5-10x inbound shift within a year |
| Today's qualified-lead leak rate (without instant Quinn) | 50% | 65% | Combination of dropped messages, response-time decay, off-hours misses |
| Leak rate with Quinn instant-qualification | 10% | 15% | Industry baseline for instant-response systems |
| Recovered → SQL conversion | 25% | 30% | Typical B2B inbound qualification rates |
| SQL → closed-won (LATAM mid-market) | 12% | 18% | Telnyx's own win rate; would pull from their pipeline data |

### ACV assumptions

| Input | Estimate | How we'd validate |
|---|---|---|
| Telnyx LATAM mid-market ACV | $20K–$50K | Telnyx pricing pages + comparable accounts in their CRM |
| Sales cycle | 60–90 days | LATAM-specific cycle from their sales ops team |

### The output

**Conservative scenario, today's volume:**
- 25 msgs/wk × 4 wk = 100 msgs/month
- Lost to leak today: 50% × 100 = 50/month
- Recovered with Quinn: (50 – 10) = 40/month
- Of those recovered, becoming SQLs: 40 × 25% = 10 SQLs/month
- Closed-won: 10 × 12% = 1.2 deals/month
- Annual: ~14 deals × $30K average = **~$420K incremental ARR**

**Optimistic scenario, post-GA (12 months out):**
- 75 msgs/wk × 5x = 1,500 msgs/month
- Recovered SQLs: 1,500 × 50% leak reduction × 30% qualification ≈ 225 SQLs/month
- Closed-won: 225 × 18% = 40 deals/month
- Annual: ~480 deals × $40K average = **~$19M incremental ARR**

Even cutting the optimistic case in half (account for Fermi error compounding), the post-GA opportunity is meaningfully large.

### Pessimistic stress-test — does it still pencil?

What if every input is much worse than estimated? Let's pressure-test:

| Input | Pessimistic value |
|---|---|
| Volume | 15 msgs/wk (60/month) |
| Leak today | 40% (Telnyx already responds to some) |
| Leak with Quinn | 15% (smaller delta) |
| SQL conversion | 20% (lower) |
| Closed-won | 12% |
| ACV | $20K (low end of mid-market) |

Math: 60 × 25% recovered × 20% SQL × 12% close-won = **0.36 deals/month → ~4.3 deals/year × $20K = ~$86K/year incremental ARR**

**Even at this floor, the project pays back in well under one quarter of one engineer's loaded cost.** And it ignores the asymmetric downside: if Telnyx ships WhatsApp Business GA without Quinn coverage, every LATAM inbound post-launch is a leak that compounds over time. The cost of NOT shipping this grows fast.

### BDR time savings (a smaller but real line)

- Average pre-qualification call: 15 min
- At 200 inbound/month (mid-range), Quinn handles initial scoring → SDR skips ~50% of qualifying questions
- Time saved: 200 × 7.5 min = 25 hours/month per SDR
- At ~$25/hr fully loaded LATAM SDR: **~$7.5K/year per SDR**, scaling with team size

---

## Hidden value (harder to quantify, real anyway)

1. **The dogfooding case study.** "Telnyx uses Telnyx for our own AI SDR" is a marketing asset for the WhatsApp Business launch. One published case study in the right channel is worth ~$50K-$200K in pipeline-attributable ARR (typical case-study ROI math).
2. **WhatsApp Business product validation.** Internal use stress-tests the API before paying customers find the bugs. Quinn becomes the first-customer feedback loop.
3. **Talent signal.** Shows future Growth Engineers + GTM AI hires that Telnyx ships its own tooling. Reduces hiring friction for similar roles.
4. **24/7 coverage without 24/7 staffing.** A LATAM SDR in São Paulo isn't online at 3am Brazil time when a Mexican CTO messages. Quinn handles the qualification + holds the warm lead until business hours.

---

## What we'd need to validate (Day-1)

In priority order:

1. **Pull actual LATAM inbound volume** from existing Telnyx logs (Salesforce, Marketo, support inbox, current SMS volume by country code). Replaces the "25-75 msgs/week" estimate with a real baseline.
2. **Measure current response-time decay** on LATAM leads — what's the actual conversion drop from 1-min vs 1-hour responses in your CRM?
3. **Confirm mid-market ACV** for LATAM specifically (often differs from US baseline due to pricing, deal size, currency).
4. **Run a 2-week pilot** with one Brazilian SDR — Quinn handles inbound, SDR handles outbound + closes. Measure SQL rate vs the 4 weeks before.

---

## TL;DR

Three scenarios, all positive ROI:

| Scenario | Annual incremental ARR | Notes |
|---|---|---|
| Pessimistic floor | ~$86K | Assumes very low volume, lower deltas, low ACV — still pays back the build inside one quarter |
| Conservative (today's volume) | ~$420K | + $7.5K/year BDR savings + dogfooding case-study value |
| Optimistic (post WhatsApp Business GA) | ~$5–19M | Depends on how much LATAM inbound shifts to WhatsApp post-launch |

- **Cost:** ~2 hours of POC build + ~1 sprint to productionize (real Telnyx WhatsApp credentials, real Salesforce API, observability)
- **Risk profile:** Low. Quinn already handles inbound; this extends the same architecture to a new channel that's launching anyway.
- **Asymmetric downside if NOT built:** every LATAM WhatsApp inbound after the WhatsApp Business GA is a leak that compounds over time.

The math holds even if every input is wrong by 2-3x. The real question isn't "is this worth building" — it's "why isn't this already shipping with the WhatsApp Business GA?"
