# Agent Line Map: Cortex PM Chief-of-Staff Agent

> Module 1 · The Agent Line

## The workflow, decision by decision

Every discrete decision/action in Cortex's workflow, scored on the three axes and placed
**above** the line (a human owns it) or **below** (Cortex owns it). Borderline calls get an
HITL checkpoint: Cortex does the work, a human approves before it proceeds.

| Decision / action | Reversibility (H/M/L) | Blast radius (H/M/L) | Measurability (H/M/L) | Above / Below | HITL? |
|---|---|---|---|---|---|
| Pull project state + recent engineering activity | H | L | H | Below | · |
| Decide which past updates / context are relevant | H | L | M | Below | · |
| Draft the weekly leadership status update | H | L | H | Below | spot-check |
| Decide tone / commitment level (e.g. promising a date) | M | M | L | Below | required |
| Flag a project as at-risk (internal signal) | H | M | M | Below | required |
| Choose which risk call to escalate to a human | M | M | M | Below | required |
| Propose next sprint's stories from the PRD (within cap) | H | L | M | Below | spot-check |
| Post the update company-wide / commit a ship date | L | H | L | Above | required |

## Agent anatomy (sketch)

- **Model:** `claude-haiku-4-5` as the cheap, fast default (a full run ≈ $0.02); a frontier
  model (Opus/Sonnet) is the escalation path if drafting quality or judgment calls ever need it.
- **Tools:** `get_project` · `get_activity` · `search_past_updates` · `get_roadmap` ·
  `get_norms` (all read-only) · `propose_stories` (queues only, capped) — there is deliberately
  **no** post / create / merge / commit-date tool.
- **Memory:** the roadmap, team norms, and past updates persist as ground truth (fixtures);
  the per-run conversation transcript is purged after each run.
- **Loop:** placeholder, defined in M2 `loop-spec.md`.
- **Bounds:** placeholder, defined in M5 `bounds-and-evals.md` (currently: 8 max iterations,
  2 max revisions, $0.50 per-run cost cap, 10-item queue cap).
- **Evals:** placeholder, defined in M5 `bounds-and-evals.md`.

## The golden rule, applied

One sentence per decision, naming the axis that decides it:

1. **Pull project state** sits *below* — read-only and checkable, so reversibility decides it; Cortex owns it.
2. **Decide relevant context** sits *below* — a wrong pick only makes a weaker draft that's cheap to correct, so blast radius keeps it below.
3. **Draft the update** sits *below* — nothing leaves the building until a human sends, so it's easy to reverse and easy to verify on read.
4. **Decide tone / commit a date** is *below with HITL* — a commitment is hard to walk back and tone is fuzzy to measure, so measurability sends it to human approval.
5. **Flag a project at-risk** is *below with HITL* — the flag is reversible but a false alarm ripples to stakeholders, so blast radius makes a human confirm it.
6. **Choose which risk to escalate** is *below with HITL* — all three axes are middling, so no single axis clears it and a human confirms.
7. **Propose a story batch** sits *below* — a proposal commits nothing and is bounded by the cap, so reversibility keeps it below.
8. **Post company-wide / commit a date** sits *above* — it's near-impossible to reverse and hits everyone at once, so reversibility puts it in human hands, always, and no demo quality changes that.

## Hardest call

**Flag a project as at-risk.** I went back and forth: the flag is trivially reversible (you just
un-flag it), which argued for *below*. But **blast radius** finally settled it — a false "at-risk"
flag reaches leadership and erodes trust in every future flag Cortex raises, and that reputational
cost is what you can't easily undo. So blast radius, not reversibility, was the deciding axis, and
it lands below the line *with a required HITL checkpoint* rather than fully autonomous.
