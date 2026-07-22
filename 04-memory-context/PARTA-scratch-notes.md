# Module 4 · Part A — SCRATCH NOTES (not the deliverable, do NOT commit)

> Rough, by-instinct draft of Cortex's memory & context plan, BEFORE the lecture.
> The real memory-and-context.md gets built in Part B.

## A1 — Brain on vs. brain off (grounding probe)
- **Brain ON** (happy path): cited real pulled data — PRs #812/#815, activation 39% → 41%,
  precedent from search_past_updates. Every claim traced to a source.
- **Brain OFF** (activity feed withheld → `activity: []`): Cortex first tried to draft green on
  stale data → the CRITIC rejected it ("green with empty activity violates the evidence norm")
  → Cortex revised to **ESCALATE** ("can't make an evidence-based call without current evidence").
- **Named gap:** the model didn't change — only the context did. Grounded = cites; ungrounded =
  refuses or over-reaches (and the critic catches the over-reach).

## A2 — Source inventory + gut call (retrieve vs include)  [MY INSTINCT — fill in]
| Source (tool) | Size | Changes | My gut call | One-line why |
|---|---|---|---|---|
| Task brief (get_task) | one short doc | new each run | **INCLUDE** | usually short summaries |
| Project record (get_project) | small | as project moves | **RETRIEVE** | (I felt it holds large historical records) — ⚠ borderline, hold this one |
| Recent activity (get_activity) | large & growing | constantly | **RETRIEVE** | there'd be lots of activity |
| Past updates & decisions (search_past_updates) | large, append-only | grows over time | **RETRIEVE** | not all past activity is relevant |
| Roadmap (get_roadmap) | medium, some confidential | changes, must stay current | **INCLUDE** | context necessary for reasoning |
| Team norms (get_norms) | medium, standing rules | rarely, must be current | **INCLUDE** | always important to keep in context |

## A3 — Remember vs. forget  [MY INSTINCT]
- **Carry across runs:** product names · product development status · product requirements
- **Forget after this run:** daily standup updates · daily blockers & dependencies
- **One way stored memory could mislead over time:** a **pricing benchmark that changes over
  time** — a STALE fact (was true, saved, now wrong but still trusted).
  (Note to self: "product development status" in my carry-across list is the SAME trap — status
  goes stale week to week; may belong in "forget & re-pull" instead. Hold for the lecture.)

## A4 — The one source I went back and forth on (hold for the lecture)
> **#2 Project record (`get_project`).** I called it RETRIEVE (thought it held large historical
> records), but it's actually a small single record. So: should a small, stable record just be
> INCLUDED whole, or RETRIEVED? Holding this one for the rubric.

Grounding-probe break point: withholding **get_activity** broke grounding → Cortex over-reached
on stale data → critic caught it → escalate.
