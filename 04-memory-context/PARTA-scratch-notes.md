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
| Source (tool) | Size | Changes | My gut call: RETRIEVE (slice) or INCLUDE (whole)? | One-line why |
|---|---|---|---|---|
| Task brief (get_task) | one short doc | new each run | ? | ? |
| Project record (get_project) | small | as project moves | ? | ? |
| Recent activity (get_activity) | large & growing | constantly | ? | ? |
| Past updates & decisions (search_past_updates) | large, append-only | grows over time | ? | ? |
| Roadmap (get_roadmap) | medium, some confidential | changes, must stay current | ? | ? |
| Team norms (get_norms) | medium, standing rules | rarely, must be current | ? | ? |

## A3 — Remember vs. forget  [MY INSTINCT — fill in]
- Carry across runs: _?_
- Forget after this run: _?_
- One way stored memory could mislead over time (stale fact / poisoned fact): _?_

## A4 — The one source I went back and forth on (hold for the lecture)
- _to be decided_
