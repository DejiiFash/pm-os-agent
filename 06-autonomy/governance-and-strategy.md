# Bounds, Trust & Autonomy Strategy: Cortex PM Chief-of-Staff Agent

> Module 6 · ★ Deliverable 5, how you'd ship it and widen trust over time

## Autonomy Dial by segment

_Autonomy is a product decision per user, not one global setting._

| Segment | Desired autonomy | Why |
|---|---|---|
| **Cautious PM ("Tesla driver")** | Supervised | Wants to read and edit every update before it goes out; values control over speed. |
| **High-trust team lead ("Waymo passenger")** | Bounded-autonomous *for assembly* | Happy to let the weekly update draft + story proposal assemble themselves — but still no posting; the HITL approval stays. |
| **Exec / company-wide comms** | Always supervised | Blast radius is company-wide and irreversible; this stays above the line permanently, regardless of track record. |

## Trust Ladder

- **Current rung:** **supervised** — Cortex drafts and proposes; a human approves everything at the HITL checkpoint. Nothing it produces takes effect on its own.
- **Eval gate to reach the next rung (bounded-autonomous for the *assembly* step only):** over a rolling 4-week window — critic `pass` rate ≥ 95% on the happy path, **zero** confidential leaks, **zero** unapproved commitments, **100%** jailbreak refusal, and cost/run within cap. The next rung still means "assembles unattended and queues for review," never "posts."
- **Incident record so far:** none in testing (fixtures + the M5 trip runs all behaved as designed).

## Deployment plan

- **Runtime:** serverless cron (a Monday-morning trigger that assembles each project's weekly update), or a managed agent platform. Serverless keeps cost near-zero between runs and makes the schedule the trigger.
- **Operator / on-call owner:** the PM who owns each project owns its Cortex output; a platform owner owns the runtime, keys, and spend cap.
- **Rollback:** disable the cron / feature-flag it off → the team falls back to writing updates manually. No data migration, because Cortex writes nothing to the world.
- **Monitoring:** a dashboard watching escalation rate, cost per run, critic `fail` rate, and — the key trust signal — the rate at which a human *overturns* the critic or heavily edits an approved draft.

## ROI metrics (beyond adoption & tokens)

| Metric | Target |
|---|---|
| Task completion rate (runs reaching DONE, grounded, critic-passed) | ≥ 90% |
| Time saved (PM hours/week not spent assembling updates) | ~2–3 hrs per PM per week |
| Trust incidents (confidential leak / unapproved commitment / bad post) | 0 |
| Human edit rate on approved drafts (proxy for draft quality) | Trending down toward < 20% |

## Widen-autonomy decision rule

Turn the dial up one notch **only when, stated in advance:** across the last 4 weeks of runs, the
critic pass rate held ≥ 95%, there were **zero** confidential leaks and **zero** unapproved
commitments, jailbreak refusal stayed 100%, and humans accepted approved drafts with only light
edits (edit rate < 20%). Any single confidential leak or unapproved commitment resets the clock and
drops the rung. Company-wide posting never earns its way below the line — it stays a human decision.
